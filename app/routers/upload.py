from fastapi import APIRouter, File, UploadFile, HTTPException, status
import os
import time
import tempfile
from typing import Optional
import shutil

from qiniu import Auth, put_file, etag

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    responses={404: {"description": "Not found"}},
)

# 七牛云配置
access_key = 'zwEq7w_iZsL3gVWshRqv6DeQAE7zw0N89BpWqevY'
secret_key = 'N2-iOl1Xixr5YZ4AxF6ntrWUnk8QUNWegaLQMNNH'
bucket_name = 'smalldu-personal'
domain = 'http://st94le9by.hn-bkt.clouddn.com'

@router.post("/", status_code=status.HTTP_200_OK)
async def upload_image(file: UploadFile = File(...), custom_key: Optional[str] = None):
    """
    上传图片到七牛云
    
    此接口将接收上传的图片文件，并将其存储到七牛云对象存储服务中。
    上传成功后返回文件的访问URL和唯一标识符。
    
    @param file: 要上传的文件，必须是图片格式（image/*）
    @param custom_key: 自定义文件名，如果不指定则使用时间戳+原始文件名
    @returns: 包含上传成功后的文件URL和key的字典
    @raises: 
        - 400 如果上传的不是图片文件
        - 400 如果上传过程中发生错误
        - 400 如果七牛云返回上传失败
    """
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, 
            detail="只允许上传图片文件"
        )
    
    # 创建临时文件
    temp_file_path = ""
    try:
        # 使用更可靠的方式创建临时文件
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file_path = temp_file.name
            # 将上传的文件内容复制到临时文件
            shutil.copyfileobj(file.file, temp_file)
        
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        
        # 如果没有指定key，使用时间戳+原始文件名
        if not custom_key:
            file_name = file.filename
            key = f"{int(time.time())}_{file_name}"
        else:
            key = custom_key
        
        # 生成上传 Token
        token = q.upload_token(bucket_name, key, 3600)
        
        # 上传文件
        ret, info = put_file(token, key, temp_file_path)
        
        # 检查是否上传成功
        if ret and ret['key'] == key and ret['hash'] == etag(temp_file_path):
            file_url = f"{domain}/{key}"
            return {"url": file_url, "key": key}
        else:
            # 记录更详细的错误信息
            error_detail = f"上传失败: 状态码={info.status_code}, 响应={info.text_body}"
            raise HTTPException(
                status_code=400, 
                detail=error_detail
            )
    except Exception as e:
        # 记录异常类型和详细信息
        error_type = type(e).__name__
        error_detail = f"上传过程中发生错误: [{error_type}] {str(e)}"
        raise HTTPException(
            status_code=400, 
            detail=error_detail
        )
    finally:
        # 确保临时文件被删除
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                # 如果删除临时文件失败，不影响主流程
                pass

@router.get("/private/{key}")
def get_private_url(key: str, expires: int = 3600):
    """
    获取私有资源的访问URL
    
    此接口根据提供的文件标识符(key)生成一个带有签名的临时访问URL，
    用于访问存储在七牛云中的私有资源。URL的有效期可以通过expires参数指定。
    
    @param key: 文件在七牛云中的唯一标识
    @param expires: 链接有效期，单位秒，默认1小时(3600秒)
    @returns: 包含带签名的私有资源URL的字典
    """
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    
    # 生成私有资源访问URL
    base_url = f"{domain}/{key}"
    
    # 生成私有URL
    private_url = q.private_download_url(base_url, expires=expires)
    
    return {"url": private_url} 