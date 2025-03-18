<template>
  <div class="categories-container">
    <div class="page-header">
      <h2><el-icon><Files /></el-icon> 分类管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新增分类
      </el-button>
    </div>

    <!-- 分类列表 -->
    <el-card shadow="hover" class="categories-card">
      <div v-loading="loading">
        <el-table
          :data="categories"
          style="width: 100%"
          border
          stripe
          highlight-current-row
          @row-click="handleRowClick"
        >
          <el-table-column prop="name" label="分类名称" min-width="150">
            <template #default="scope">
              <span class="category-name">{{ scope.row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="250">
            <template #default="scope">
              <span class="category-desc">{{ scope.row.description || '暂无描述' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="180">
            <template #default="scope">
              <span>{{ formatDate(scope.row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-button
                size="small"
                type="primary"
                @click.stop="openDialog(scope.row)"
              >
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-popconfirm
                title="确定删除该分类吗？"
                @confirm="deleteCategory(scope.row.id)"
                @click.stop
              >
                <template #reference>
                  <el-button size="small" type="danger">
                    <el-icon><Delete /></el-icon> 删除
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 分类表单对话框 -->
    <el-dialog
      :title="isEdit ? '编辑分类' : '新增分类'"
      v-model="dialogVisible"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="categoryForm" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Files, Plus, Edit, Delete } from '@element-plus/icons-vue'
import api from '@/api'

export default {
  name: 'Categories',
  components: {
    Files,
    Plus,
    Edit,
    Delete
  },
  setup() {
    const categories = ref([])
    const loading = ref(false)
    const dialogVisible = ref(false)
    const isEdit = ref(false)
    const categoryForm = ref(null)
    
    const form = reactive({
      id: '',
      name: '',
      description: ''
    })
    
    const rules = {
      name: [
        { required: true, message: '请输入分类名称', trigger: 'blur' },
        { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
      ]
    }

    /**
     * 获取分类列表
     */
    const fetchCategories = async () => {
      loading.value = true
      try {
        const response = await api.get('/categories/')
        categories.value = response.data || []
      } catch (error) {
        ElMessage.error('获取分类列表失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    /**
     * 打开对话框
     * @param {Object} category - 要编辑的分类对象
     */
    const openDialog = (category) => {
      resetForm()
      if (category) {
        isEdit.value = true
        form.id = category.id
        form.name = category.name
        form.description = category.description || ''
      } else {
        isEdit.value = false
      }
      dialogVisible.value = true
    }

    /**
     * 重置表单
     */
    const resetForm = () => {
      form.id = ''
      form.name = ''
      form.description = ''
      if (categoryForm.value) {
        categoryForm.value.resetFields()
      }
    }

    /**
     * 提交表单
     */
    const submitForm = async () => {
      if (!categoryForm.value) return
      
      await categoryForm.value.validate(async (valid) => {
        if (valid) {
          try {
            if (isEdit.value) {
              await api.put(`/categories/${form.id}`, {
                name: form.name,
                description: form.description
              })
              ElMessage.success('更新分类成功')
            } else {
              await api.post('/categories/', {
                name: form.name,
                description: form.description
              })
              ElMessage.success('创建分类成功')
            }
            dialogVisible.value = false
            fetchCategories()
          } catch (error) {
            ElMessage.error(isEdit.value ? '更新分类失败' : '创建分类失败')
            console.error(error)
          }
        }
      })
    }

    /**
     * 删除分类
     * @param {string} id - 分类ID
     */
    const deleteCategory = async (id) => {
      try {
        await api.delete(`/categories/${id}`)
        ElMessage.success('删除分类成功')
        fetchCategories()
      } catch (error) {
        ElMessage.error('删除分类失败')
        console.error(error)
      }
    }

    /**
     * 处理行点击
     */
    const handleRowClick = (row) => {
      console.log('点击行:', row)
      // 可以在这里添加行点击的逻辑，例如显示详情等
    }

    /**
     * 格式化日期
     */
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }

    onMounted(() => {
      fetchCategories()
    })

    return {
      categories,
      loading,
      dialogVisible,
      isEdit,
      form,
      rules,
      categoryForm,
      openDialog,
      submitForm,
      deleteCategory,
      handleRowClick,
      formatDate
    }
  }
}
</script>

<style scoped>
.categories-container {
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
  color: #409eff;
}

.categories-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.category-name {
  font-weight: bold;
  color: #303133;
}

.category-desc {
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: bold;
}

:deep(.el-table tr:hover) {
  background-color: #f0f9ff;
}
</style> 