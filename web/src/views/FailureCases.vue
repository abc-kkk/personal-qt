<template>
  <div class="failure-cases-container">
    <div class="page-header">
      <h2><el-icon><Warning /></el-icon> 失败案例</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新增失败案例
      </el-button>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-container">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterForm.categoryId" placeholder="选择分类" clearable>
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchFailureCases">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><RefreshRight /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 失败案例卡片列表 -->
    <div v-loading="loading">
      <el-empty v-if="failureCases.length === 0" description="暂无失败案例"></el-empty>
      <el-row :gutter="24" v-else>
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in failureCases" :key="item.id" class="card-col">
          <el-card class="failure-card" shadow="hover" @click="viewDetail(item)">
            <div class="card-image" v-if="item.images && item.images.length > 0">
              <el-image :src="item.images[0]" fit="cover"></el-image>
            </div>
            <div class="card-content">
              <h3>{{ item.stock_name }} <span class="stock-code">({{ item.stock_code }})</span></h3>
              <p class="reason">{{ truncateText(item.reason, 50) }}</p>
              <p class="lessons">{{ truncateText(item.lessons, 80) }}</p>
            </div>
            <div class="card-actions">
              <el-button size="small" type="primary" @click.stop="openDialog(item)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-popconfirm
                title="确定删除该失败案例吗？"
                @confirm="deleteFailureCase(item.id)"
                @click.stop
              >
                <template #reference>
                  <el-button size="small" type="danger">
                    <el-icon><Delete /></el-icon> 删除
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 失败案例表单对话框 -->
    <el-dialog
      :title="isEdit ? '编辑失败案例' : '新增失败案例'"
      v-model="dialogVisible"
      width="650px"
    >
      <el-form :model="form" :rules="rules" ref="failureCaseForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="股票代码" prop="stock_code">
              <el-input v-model="form.stock_code" placeholder="请输入股票代码"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="股票名称" prop="stock_name">
              <el-input v-model="form.stock_name" placeholder="请输入股票名称"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="失败理由" prop="reason">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入失败理由"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="教训总结" prop="lessons">
          <el-input
            v-model="form.lessons"
            type="textarea"
            :rows="3"
            placeholder="请输入教训总结"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="截图">
          <el-upload
            action="#"
            list-type="picture-card"
            :file-list="fileList"
            :on-change="handleFileChange"
            :auto-upload="false"
            :on-remove="handleRemove"
            :on-preview="handlePreview"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      title="失败案例详情"
      v-model="detailVisible"
      width="800px"
    >
      <div v-if="currentCase" class="detail-container">
        <h2>{{ currentCase.stock_name }} ({{ currentCase.stock_code }})</h2>
        
        <div class="detail-section">
          <h3>失败理由</h3>
          <p>{{ currentCase.reason }}</p>
        </div>
        
        <div class="detail-section">
          <h3>教训总结</h3>
          <p>{{ currentCase.lessons }}</p>
        </div>
        
        <div class="detail-section" v-if="currentCase.images && currentCase.images.length > 0">
          <h3>相关截图</h3>
          <div class="image-gallery">
            <el-image 
              v-for="(image, index) in currentCase.images" 
              :key="index"
              :src="image"
              :preview-src-list="currentCase.images"
              fit="contain"
              class="gallery-image"
            ></el-image>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 图片预览 -->
    <el-dialog v-model="previewVisible" title="图片预览">
      <img :src="previewUrl" alt="Preview" style="width: 100%;" />
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Edit, Delete, Warning, Search, RefreshRight } from '@element-plus/icons-vue'
import api from '@/api'

export default {
  name: 'FailureCases',
  components: {
    Plus,
    Edit,
    Delete,
    Warning,
    Search,
    RefreshRight
  },
  setup() {
    const failureCases = ref([])
    const loading = ref(false)
    const dialogVisible = ref(false)
    const detailVisible = ref(false)
    const isEdit = ref(false)
    const failureCaseForm = ref(null)
    const currentCase = ref(null)
    const previewVisible = ref(false)
    const previewUrl = ref('')
    const fileList = ref([])
    const categories = ref([])
    
    const filterForm = reactive({
      dateRange: [],
      categoryId: ''
    })
    
    const form = reactive({
      id: '',
      stock_code: '',
      stock_name: '',
      reason: '',
      lessons: '',
      images: []
    })
    
    const rules = {
      stock_code: [{ required: true, message: '请输入股票代码', trigger: 'blur' }],
      stock_name: [{ required: true, message: '请输入股票名称', trigger: 'blur' }],
      reason: [{ required: true, message: '请输入失败理由', trigger: 'blur' }],
      lessons: [{ required: true, message: '请输入教训总结', trigger: 'blur' }]
    }

    /**
     * 获取失败案例列表
     */
    const fetchFailureCases = async () => {
      loading.value = true
      try {
        // 构建查询参数
        const params = {}
        if (filterForm.dateRange && filterForm.dateRange.length === 2) {
          params.start_date = filterForm.dateRange[0]
          params.end_date = filterForm.dateRange[1]
        }
        if (filterForm.categoryId) {
          params.category_id = filterForm.categoryId
        }
        
        const response = await api.get('/failure-cases/', { params })
        console.log('失败案例响应:', response)
        failureCases.value = response.data || []
      } catch (error) {
        ElMessage.error('获取失败案例列表失败')
        console.error('获取失败案例错误:', error)
      } finally {
        loading.value = false
      }
    }

    /**
     * 获取分类列表
     */
    const fetchCategories = async () => {
      try {
        const response = await api.get('/categories/')
        categories.value = response.data || []
      } catch (error) {
        ElMessage.error('获取分类列表失败')
        console.error(error)
      }
    }

    /**
     * 打开对话框
     * @param {Object} failureCase - 要编辑的失败案例对象
     */
    const openDialog = (failureCase) => {
      resetForm()
      if (failureCase) {
        isEdit.value = true
        form.id = failureCase.id
        form.stock_code = failureCase.stock_code
        form.stock_name = failureCase.stock_name
        form.reason = failureCase.reason
        form.lessons = failureCase.lessons
        form.images = failureCase.images || []
        
        // 设置文件列表
        fileList.value = (failureCase.images || []).map((url, index) => ({
          name: `截图${index + 1}`,
          url: url
        }))
      } else {
        isEdit.value = false
        fileList.value = []
      }
      dialogVisible.value = true
    }

    /**
     * 查看详情
     * @param {Object} failureCase - 要查看的失败案例对象
     */
    const viewDetail = (failureCase) => {
      currentCase.value = failureCase
      detailVisible.value = true
    }

    /**
     * 重置表单
     */
    const resetForm = () => {
      form.id = ''
      form.stock_code = ''
      form.stock_name = ''
      form.reason = ''
      form.lessons = ''
      form.images = []
      
      if (failureCaseForm.value) {
        failureCaseForm.value.resetFields()
      }
    }

    /**
     * 提交表单
     */
    const submitForm = async () => {
      if (!failureCaseForm.value) return
      
      await failureCaseForm.value.validate(async (valid) => {
        if (valid) {
          try {
            const data = {
              stock_code: form.stock_code,
              stock_name: form.stock_name,
              reason: form.reason,
              lessons: form.lessons,
              images: form.images
            }
            
            console.log('提交失败案例数据:', data)
            
            if (isEdit.value) {
              await api.put(`/failure-cases/${form.id}`, data)
              ElMessage.success('更新失败案例成功')
            } else {
              await api.post('/failure-cases/', data)
              ElMessage.success('创建失败案例成功')
            }
            dialogVisible.value = false
            fetchFailureCases()
          } catch (error) {
            ElMessage.error(isEdit.value ? '更新失败案例失败' : '创建失败案例失败')
            console.error('提交失败案例错误:', error)
          }
        }
      })
    }

    /**
     * 删除失败案例
     * @param {string} id - 失败案例ID
     */
    const deleteFailureCase = async (id) => {
      try {
        await api.delete(`/failure-cases/${id}`)
        ElMessage.success('删除失败案例成功')
        fetchFailureCases()
      } catch (error) {
        ElMessage.error('删除失败案例失败')
        console.error(error)
      }
    }

    /**
     * 处理文件变更
     * @param {Object} file - 变更的文件对象
     */
    const handleFileChange = (file) => {
      // 静态示例URL，在GitHub Pages上不能真正上传图片
      const reader = new FileReader()
      reader.onload = (e) => {
        form.images.push(e.target.result)
      }
      reader.readAsDataURL(file.raw)
    }

    /**
     * 处理移除文件
     * @param {Object} file - 文件对象
     */
    const handleRemove = (file) => {
      const index = fileList.value.indexOf(file)
      if (index !== -1) {
        form.images.splice(index, 1)
        fileList.value.splice(index, 1)
      }
    }

    /**
     * 处理预览
     * @param {Object} file - 文件对象
     */
    const handlePreview = (file) => {
      previewUrl.value = file.url
      previewVisible.value = true
    }

    /**
     * 截断文本
     * @param {string} text - 要截断的文本
     * @param {number} length - 最大长度
     * @returns {string} 截断后的文本
     */
    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    /**
     * 重置筛选条件
     */
    const resetFilter = () => {
      filterForm.dateRange = []
      filterForm.categoryId = ''
      fetchFailureCases()
    }

    onMounted(() => {
      fetchFailureCases()
      fetchCategories()
    })

    return {
      failureCases,
      loading,
      dialogVisible,
      detailVisible,
      isEdit,
      form,
      rules,
      failureCaseForm,
      currentCase,
      fileList,
      previewVisible,
      previewUrl,
      filterForm,
      openDialog,
      viewDetail,
      submitForm,
      deleteFailureCase,
      handleFileChange,
      handleRemove,
      handlePreview,
      truncateText,
      resetFilter,
      categories
    }
  }
}
</script>

<style scoped>
.failure-cases-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  display: flex;
  align-items: center;
}

.page-header h2 .el-icon {
  margin-right: 8px;
  font-size: 24px;
  color: #f56c6c;
}

.filter-container {
  background-color: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.card-col {
  margin-bottom: 24px;
}

.failure-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.failure-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-image {
  height: 180px;
  overflow: hidden;
}

.card-image .el-image {
  width: 100%;
  height: 100%;
  transition: transform 0.3s;
}

.failure-card:hover .card-image .el-image {
  transform: scale(1.05);
}

.card-content {
  padding: 16px;
  flex-grow: 1;
}

.card-content h3 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 18px;
  color: #303133;
}

.stock-code {
  color: #909399;
  font-weight: normal;
  font-size: 0.9em;
}

.reason, .lessons {
  margin: 8px 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.reason {
  font-weight: bold;
}

.card-actions {
  display: flex;
  justify-content: space-between;
  padding: 0 16px 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

.detail-container {
  padding: 0 20px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h3 {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 12px;
  margin-bottom: 16px;
  color: #303133;
}

.image-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.gallery-image {
  width: 200px;
  height: 150px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.gallery-image:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
}
</style> 