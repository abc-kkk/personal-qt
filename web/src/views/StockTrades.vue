<template>
  <div class="stock-trades-container">
    <div class="page-header">
      <h2>交易记录</h2>
      <el-button type="primary" @click="openDialog()">新增交易记录</el-button>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="filter-container">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="买入时间">
          <el-date-picker
            v-model="filterForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          ></el-date-picker>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterForm.categoryId" placeholder="选择分类" clearable style="width: 220px;">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchStockTrades">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 交易记录表格 -->
    <el-table :data="stockTrades" style="width: 100%" v-loading="loading">
      <el-table-column prop="stock_code" label="股票代码" width="100"></el-table-column>
      <el-table-column prop="stock_name" label="股票名称" width="120"></el-table-column>
      <el-table-column label="买入时间" width="120">
        <template #default="scope">
          {{ formatDate(scope.row.buy_date) }}
        </template>
      </el-table-column>
      <el-table-column prop="buy_price" label="买入价格" width="100"></el-table-column>
      <el-table-column prop="buy_quantity" label="买入数量" width="100"></el-table-column>
      <el-table-column label="卖出时间" width="120">
        <template #default="scope">
          {{ scope.row.sell_date ? formatDate(scope.row.sell_date) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="sell_price" label="卖出价格" width="100">
        <template #default="scope">
          {{ scope.row.sell_price || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="涨跌幅" width="100">
        <template #default="scope">
          <span :class="getChangeRateClass(scope.row)">
            {{ calculateChangeRate(scope.row) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="盈亏金额" width="120">
        <template #default="scope">
          <span :class="getProfitClass(scope.row)">
            {{ calculateProfit(scope.row) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="分类" width="120">
        <template #default="scope">
          {{ getCategoryName(scope.row.category_id) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="scope">
          <el-button size="small" @click="openDialog(scope.row)">编辑</el-button>
          <el-popconfirm
            title="确定删除该交易记录吗？"
            @confirm="deleteStockTrade(scope.row.id)"
          >
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 统计信息 -->
    <div class="statistics-container" v-if="stockTrades.length > 0">
      <div class="statistic-item">
        <span class="label">总交易笔数:</span>
        <span class="value">{{ stockTrades.length }}</span>
      </div>
      <div class="statistic-item">
        <span class="label">总盈亏幅度:</span>
        <span :class="getTotalChangeRateClass()">{{ calculateTotalChangeRate() }}</span>
      </div>
      <div class="statistic-item">
        <span class="label">总盈亏金额:</span>
        <span :class="getTotalProfitClass()">{{ calculateTotalProfit() }}</span>
      </div>
    </div>

    <!-- 交易记录表单对话框 -->
    <el-dialog
      :title="isEdit ? '编辑交易记录' : '新增交易记录'"
      v-model="dialogVisible"
      width="650px"
    >
      <el-form :model="form" :rules="rules" ref="stockTradeForm" label-width="100px">
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
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="买入时间" prop="buy_date">
              <el-date-picker
                v-model="form.buy_date"
                type="datetime"
                placeholder="选择买入时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
              ></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类" prop="category_id">
              <el-select v-model="form.category_id" placeholder="选择分类" style="width: 220px;">
                <el-option
                  v-for="item in categories"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="买入价格" prop="buy_price">
              <el-input-number
                v-model="form.buy_price"
                :precision="2"
                :step="0.01"
                :min="0"
                placeholder="请输入买入价格"
              ></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="买入数量" prop="buy_quantity">
              <el-input-number
                v-model="form.buy_quantity"
                :precision="0"
                :step="100"
                :min="0"
                placeholder="请输入买入数量"
              ></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="卖出时间" prop="sell_date">
              <el-date-picker
                v-model="form.sell_date"
                type="datetime"
                placeholder="选择卖出时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                clearable
              ></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="卖出价格" prop="sell_price">
              <el-input-number
                v-model="form.sell_price"
                :precision="2"
                :step="0.01"
                :min="0"
                placeholder="请输入卖出价格"
                clearable
              ></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="买入理由" prop="buy_reason">
          <el-input
            v-model="form.buy_reason"
            type="textarea"
            :rows="3"
            placeholder="请输入买入理由"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="截图">
          <el-upload
            action="/api/upload"
            list-type="picture-card"
            :file-list="fileList"
            :on-success="handleUploadSuccess"
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

    <!-- 图片预览 -->
    <el-dialog v-model="previewVisible" title="图片预览">
      <img :src="previewUrl" alt="Preview" style="width: 100%;" />
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

export default {
  name: 'StockTrades',
  components: {
    Plus
  },
  setup() {
    const stockTrades = ref([])
    const categories = ref([])
    const loading = ref(false)
    const dialogVisible = ref(false)
    const isEdit = ref(false)
    const stockTradeForm = ref(null)
    const previewVisible = ref(false)
    const previewUrl = ref('')
    const fileList = ref([])
    
    const filterForm = reactive({
      dateRange: [],
      categoryId: ''
    })
    
    const form = reactive({
      id: '',
      stock_code: '',
      stock_name: '',
      buy_date: '',
      buy_price: null,
      buy_quantity: null,
      sell_date: '',
      sell_price: null,
      screenshot_url: [],
      buy_reason: '',
      category_id: ''
    })
    
    const rules = {
      stock_code: [{ required: true, message: '请输入股票代码', trigger: 'blur' }],
      stock_name: [{ required: true, message: '请输入股票名称', trigger: 'blur' }],
      buy_date: [{ required: true, message: '请选择买入时间', trigger: 'change' }],
      buy_price: [{ required: true, message: '请输入买入价格', trigger: 'blur' }],
      buy_quantity: [{ required: true, message: '请输入买入数量', trigger: 'blur' }],
      buy_reason: [{ required: true, message: '请输入买入理由', trigger: 'blur' }],
      category_id: [{ required: true, message: '请选择分类', trigger: 'change' }]
    }

    /**
     * 获取交易记录列表
     */
    const fetchStockTrades = async () => {
      loading.value = true
      try {
        let params = {}
        
        if (filterForm.dateRange && filterForm.dateRange.length === 2) {
          params.start_date = filterForm.dateRange[0]
          params.end_date = filterForm.dateRange[1]
        }
        
        if (filterForm.categoryId) {
          params.category_id = filterForm.categoryId
        }
        
        const response = await api.get('/stock-trades/', { params })
        stockTrades.value = response.data || []
      } catch (error) {
        ElMessage.error('获取交易记录列表失败')
        console.error(error)
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
     * @param {Object} stockTrade - 要编辑的交易记录对象
     */
    const openDialog = (stockTrade) => {
      resetForm()
      if (stockTrade) {
        isEdit.value = true
        form.id = stockTrade.id
        form.stock_code = stockTrade.stock_code
        form.stock_name = stockTrade.stock_name
        form.buy_date = stockTrade.buy_date
        form.buy_price = stockTrade.buy_price
        form.buy_quantity = stockTrade.buy_quantity
        form.sell_date = stockTrade.sell_date || ''
        form.sell_price = stockTrade.sell_price || null
        form.buy_reason = stockTrade.buy_reason
        form.category_id = stockTrade.category_id
        form.screenshot_url = stockTrade.screenshot_url || []
        
        // 设置文件列表
        fileList.value = (stockTrade.screenshot_url || []).map((url, index) => ({
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
     * 重置表单
     */
    const resetForm = () => {
      form.id = ''
      form.stock_code = ''
      form.stock_name = ''
      form.buy_date = ''
      form.buy_price = null
      form.buy_quantity = null
      form.sell_date = ''
      form.sell_price = null
      form.screenshot_url = []
      form.buy_reason = ''
      form.category_id = ''
      
      if (stockTradeForm.value) {
        stockTradeForm.value.resetFields()
      }
    }

    /**
     * 重置筛选条件
     */
    const resetFilter = () => {
      filterForm.dateRange = []
      filterForm.categoryId = ''
      fetchStockTrades()
    }

    /**
     * 提交表单
     */
    const submitForm = async () => {
      if (!stockTradeForm.value) return
      
      await stockTradeForm.value.validate(async (valid) => {
        if (valid) {
          try {
            const data = {
              stock_code: form.stock_code,
              stock_name: form.stock_name,
              buy_date: form.buy_date,
              buy_price: form.buy_price,
              buy_quantity: form.buy_quantity,
              sell_date: form.sell_date || null,
              sell_price: form.sell_price || null,
              screenshot_url: form.screenshot_url,
              buy_reason: form.buy_reason,
              category_id: form.category_id
            }
            
            if (isEdit.value) {
              await api.put(`/stock-trades/${form.id}`, data)
              ElMessage.success('更新交易记录成功')
            } else {
              await api.post('/stock-trades/', data)
              ElMessage.success('创建交易记录成功')
            }
            dialogVisible.value = false
            fetchStockTrades()
          } catch (error) {
            ElMessage.error(isEdit.value ? '更新交易记录失败' : '创建交易记录失败')
            console.error(error)
          }
        }
      })
    }

    /**
     * 删除交易记录
     * @param {string} id - 交易记录ID
     */
    const deleteStockTrade = async (id) => {
      try {
        await api.delete(`/stock-trades/${id}`)
        ElMessage.success('删除交易记录成功')
        fetchStockTrades()
      } catch (error) {
        ElMessage.error('删除交易记录失败')
        console.error(error)
      }
    }

    /**
     * 处理上传成功
     * @param {Object} response - 上传响应
     * @param {Object} file - 文件对象
     */
    const handleUploadSuccess = (response, file) => {
      form.screenshot_url.push(response.url)
    }

    /**
     * 处理移除文件
     * @param {Object} file - 文件对象
     */
    const handleRemove = (file) => {
      const index = fileList.value.indexOf(file)
      if (index !== -1) {
        form.screenshot_url.splice(index, 1)
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
     * 获取分类名称
     * @param {string} categoryId - 分类ID
     * @returns {string} 分类名称
     */
    const getCategoryName = (categoryId) => {
      const category = categories.value.find(c => c.id === categoryId)
      return category ? category.name : '-'
    }

    /**
     * 计算涨跌幅
     * @param {Object} trade - 交易记录
     * @returns {string} 涨跌幅
     */
    const calculateChangeRate = (trade) => {
      if (!trade.sell_price || !trade.buy_price) return '-'
      const rate = ((trade.sell_price - trade.buy_price) / trade.buy_price * 100).toFixed(2)
      return `${rate}%`
    }

    /**
     * 获取涨跌幅样式类
     * @param {Object} trade - 交易记录
     * @returns {string} 样式类名
     */
    const getChangeRateClass = (trade) => {
      if (!trade.sell_price || !trade.buy_price) return ''
      const rate = (trade.sell_price - trade.buy_price) / trade.buy_price
      return rate > 0 ? 'profit' : rate < 0 ? 'loss' : ''
    }

    /**
     * 计算盈亏金额
     * @param {Object} trade - 交易记录
     * @returns {string} 盈亏金额
     */
    const calculateProfit = (trade) => {
      if (!trade.sell_price || !trade.buy_price || !trade.buy_quantity) return '-'
      const profit = ((trade.sell_price - trade.buy_price) * trade.buy_quantity).toFixed(2)
      return profit
    }

    /**
     * 获取盈亏金额样式类
     * @param {Object} trade - 交易记录
     * @returns {string} 样式类名
     */
    const getProfitClass = (trade) => {
      if (!trade.sell_price || !trade.buy_price) return ''
      const profit = (trade.sell_price - trade.buy_price) * trade.buy_quantity
      return profit > 0 ? 'profit' : profit < 0 ? 'loss' : ''
    }

    /**
     * 计算总涨跌幅
     * @returns {string} 总涨跌幅
     */
    const calculateTotalChangeRate = () => {
      const soldTrades = stockTrades.value.filter(t => t.sell_price && t.buy_price)
      if (soldTrades.length === 0) return '0.00%'
      
      const totalBuyValue = soldTrades.reduce((sum, t) => sum + t.buy_price * t.buy_quantity, 0)
      const totalSellValue = soldTrades.reduce((sum, t) => sum + t.sell_price * t.buy_quantity, 0)
      
      const rate = ((totalSellValue - totalBuyValue) / totalBuyValue * 100).toFixed(2)
      return `${rate}%`
    }

    /**
     * 获取总涨跌幅样式类
     * @returns {string} 样式类名
     */
    const getTotalChangeRateClass = () => {
      const rate = parseFloat(calculateTotalChangeRate())
      return rate > 0 ? 'profit' : rate < 0 ? 'loss' : ''
    }

    /**
     * 计算总盈亏金额
     * @returns {string} 总盈亏金额
     */
    const calculateTotalProfit = () => {
      const soldTrades = stockTrades.value.filter(t => t.sell_price && t.buy_price)
      const totalProfit = soldTrades.reduce((sum, t) => {
        return sum + (t.sell_price - t.buy_price) * t.buy_quantity
      }, 0)
      
      return totalProfit.toFixed(2)
    }

    /**
     * 获取总盈亏金额样式类
     * @returns {string} 样式类名
     */
    const getTotalProfitClass = () => {
      const profit = parseFloat(calculateTotalProfit())
      return profit > 0 ? 'profit' : profit < 0 ? 'loss' : ''
    }

    /**
     * 格式化日期
     * @param {string} dateString - 日期字符串
     * @returns {string} 格式化后的日期字符串
     */
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    onMounted(() => {
      fetchCategories()
      fetchStockTrades()
    })

    return {
      stockTrades,
      categories,
      loading,
      dialogVisible,
      isEdit,
      form,
      rules,
      stockTradeForm,
      filterForm,
      fileList,
      previewVisible,
      previewUrl,
      openDialog,
      submitForm,
      deleteStockTrade,
      fetchStockTrades,
      resetFilter,
      handleUploadSuccess,
      handleRemove,
      handlePreview,
      getCategoryName,
      calculateChangeRate,
      getChangeRateClass,
      calculateProfit,
      getProfitClass,
      calculateTotalChangeRate,
      getTotalChangeRateClass,
      calculateTotalProfit,
      getTotalProfitClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.stock-trades-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filter-container {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

.statistics-container {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  display: flex;
  justify-content: space-around;
}

.statistic-item {
  text-align: center;
}

.statistic-item .label {
  font-weight: bold;
  margin-right: 10px;
}

.profit {
  color: #f56c6c;
}

.loss {
  color: #67c23a;
}

/* 确保下拉选项宽度与选择框匹配 */
:deep(.el-select-dropdown) {
  min-width: 220px !important;
}
</style> 