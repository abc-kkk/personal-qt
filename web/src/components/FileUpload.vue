/**
 * 处理文件上传
 * @param {Object} uploadFile - 上传的文件对象
 */
const handleUpload = async (uploadFile) => {
  if (!uploadFile) return
  
  const formData = new FormData()
  formData.append('file', uploadFile.raw)
  
  try {
    uploading.value = true
    const response = await api.post('/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    const fileUrl = response.data.url
    emit('success', fileUrl)
    ElMessage.success('文件上传成功')
  } catch (error) {
    ElMessage.error('文件上传失败')
    console.error(error)
    emit('error', error)
  } finally {
    uploading.value = false
  }
} 