<template>
  <div class="trading-systems-container">
    <div class="page-header">
      <h2><el-icon><Document /></el-icon> 交易系统</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新增交易系统
      </el-button>
    </div>

    <!-- 交易系统列表 -->
    <el-card shadow="hover" class="trading-systems-card">
      <div v-loading="loading">
        <el-table
          :data="tradingSystems"
          style="width: 100%"
          border
          stripe
          highlight-current-row
          @row-click="handleRowClick"
        >
          <el-table-column prop="title" label="标题" min-width="150">
            <template #default="scope">
              <span class="trading-system-title">{{ scope.row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="content" label="内容" min-width="250">
            <template #default="scope">
              <span class="trading-system-content">{{ truncateText(scope.row.content, 100) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'info'">
                {{ scope.row.is_active ? '已启用' : '已禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="sort_order" label="排序" width="80" align="center">
            <template #default="scope">
              <span>{{ scope.row.sort_order }}</span>
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
                title="确定删除该交易系统吗？"
                @confirm="deleteTradingSystem(scope.row.id)"
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

    <!-- 交易系统表单对话框 -->
    <el-dialog
      :title="isEdit ? '编辑交易系统' : '新增交易系统'"
      v-model="dialogVisible"
      width="600px"
      top="50px"
    >
      <el-form :model="form" :rules="rules" ref="tradingSystemForm" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入交易系统标题"></el-input>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="8"
            placeholder="请输入交易系统内容"
          ></el-input>
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用"></el-switch>
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="9999"></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 交易系统详情对话框 -->
    <el-dialog
      title="交易系统详情"
      v-model="detailDialogVisible"
      width="700px"
      top="50px"
    >
      <div v-if="currentSystem" class="trading-system-detail">
        <h3 class="detail-title">{{ currentSystem.title }}</h3>
        <div class="detail-meta">
          <el-tag :type="currentSystem.is_active ? 'success' : 'info'" size="small">
            {{ currentSystem.is_active ? '已启用' : '已禁用' }}
          </el-tag>
          <span class="detail-time">创建时间: {{ formatDate(currentSystem.created_at) }}</span>
          <span class="detail-time">更新时间: {{ formatDate(currentSystem.updated_at) }}</span>
        </div>
        <div class="detail-content">
          <pre>{{ currentSystem.content }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Plus, Edit, Delete } from '@element-plus/icons-vue'
import api from '@/api'

export default {
  name: 'TradingSystems',
  components: {
    Document,
    Plus,
    Edit,
    Delete
  },
  setup() {
    const tradingSystems = ref([])
    const loading = ref(false)
    const dialogVisible = ref(false)
    const detailDialogVisible = ref(false)
    const isEdit = ref(false)
    const tradingSystemForm = ref(null)
    const currentSystem = ref(null)
    
    const form = reactive({
      id: '',
      title: '',
      content: '',
      is_active: true,
      sort_order: 0
    })
    
    const rules = {
      title: [
        { required: true, message: '请输入交易系统标题', trigger: 'blur' },
        { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
      ],
      content: [
        { required: true, message: '请输入交易系统内容', trigger: 'blur' }
      ]
    }

    /**
     * 获取交易系统列表
     */
    const fetchTradingSystems = async () => {
      loading.value = true
      try {
        const response = await api.get('/trading-systems/')
        tradingSystems.value = response.data || []
      } catch (error) {
        ElMessage.error('获取交易系统列表失败')
        console.error(error)
      } finally {
        loading.value = false
      }
    }

    /**
     * 打开对话框
     * @param {Object} tradingSystem - 要编辑的交易系统对象
     */
    const openDialog = (tradingSystem) => {
      resetForm()
      if (tradingSystem) {
        isEdit.value = true
        form.id = tradingSystem.id
        form.title = tradingSystem.title
        form.content = tradingSystem.content
        form.is_active = tradingSystem.is_active
        form.sort_order = tradingSystem.sort_order
      } else {
        isEdit.value = false
      }
      dialogVisible.value = true
    }

    /**
     * 处理行点击事件，显示详情
     * @param {Object} row - 行数据
     */
    const handleRowClick = (row) => {
      currentSystem.value = row
      detailDialogVisible.value = true
    }

    /**
     * 重置表单
     */
    const resetForm = () => {
      form.id = ''
      form.title = ''
      form.content = ''
      form.is_active = true
      form.sort_order = 0
    }

    /**
     * 提交表单
     */
    const submitForm = async () => {
      tradingSystemForm.value?.validate(async (valid) => {
        if (valid) {
          try {
            if (isEdit.value) {
              // 编辑交易系统
              await api.put(`/trading-systems/${form.id}`, {
                title: form.title,
                content: form.content,
                is_active: form.is_active,
                sort_order: form.sort_order
              })
              ElMessage.success('交易系统更新成功')
            } else {
              // 创建交易系统
              await api.post('/trading-systems/', {
                title: form.title,
                content: form.content,
                is_active: form.is_active,
                sort_order: form.sort_order
              })
              ElMessage.success('交易系统创建成功')
            }
            dialogVisible.value = false
            fetchTradingSystems()
          } catch (error) {
            ElMessage.error(isEdit.value ? '更新交易系统失败' : '创建交易系统失败')
            console.error(error)
          }
        }
      })
    }

    /**
     * 删除交易系统
     * @param {string} id - 交易系统ID
     */
    const deleteTradingSystem = async (id) => {
      try {
        await api.delete(`/trading-systems/${id}`)
        ElMessage.success('交易系统删除成功')
        fetchTradingSystems()
      } catch (error) {
        ElMessage.error('删除交易系统失败')
        console.error(error)
      }
    }

    /**
     * 格式化日期
     * @param {string} dateString - ISO日期字符串
     * @returns {string} 格式化后的日期字符串
     */
    const formatDate = (dateString) => {
      if (!dateString) return '—'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    /**
     * 截断文本
     * @param {string} text - 原始文本
     * @param {number} length - 截断长度
     * @returns {string} 截断后的文本
     */
    const truncateText = (text, length) => {
      if (!text) return '—'
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    onMounted(() => {
      fetchTradingSystems()
    })

    return {
      tradingSystems,
      loading,
      dialogVisible,
      detailDialogVisible,
      isEdit,
      form,
      rules,
      currentSystem,
      tradingSystemForm,
      openDialog,
      handleRowClick,
      submitForm,
      deleteTradingSystem,
      formatDate,
      truncateText
    }
  }
}
</script>

<style scoped>
.trading-systems-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  display: flex;
  align-items: center;
  font-size: 20px;
  margin: 0;
}

.page-header h2 .el-icon {
  margin-right: 8px;
}

.trading-systems-card {
  margin-bottom: 20px;
}

.trading-system-title {
  font-weight: 500;
}

.trading-system-content {
  color: #606266;
  white-space: pre-wrap;
}

.dialog-footer {
  text-align: right;
  display: block;
}

.trading-system-detail {
  padding: 0 10px;
}

.detail-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.detail-meta {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  color: #909399;
  font-size: 14px;
}

.detail-meta .el-tag {
  margin-right: 15px;
}

.detail-time {
  margin-right: 15px;
}

.detail-content {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.detail-content pre {
  white-space: pre-wrap;
  font-family: inherit;
  line-height: 1.6;
}
</style> 