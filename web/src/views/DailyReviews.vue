<template>
  <div class="daily-reviews-container">
    <div class="page-header">
      <h2><el-icon><Calendar /></el-icon> 每日复盘</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新增复盘记录
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
        <el-form-item>
          <el-button type="primary" @click="fetchDailyReviews">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><RefreshRight /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 复盘记录列表 -->
    <div v-loading="loading">
      <el-empty v-if="dailyReviews.length === 0" description="暂无复盘记录"></el-empty>
      <el-timeline v-else>
        <el-timeline-item
          v-for="item in dailyReviews"
          :key="item.id"
          :timestamp="formatDate(item.review_date)"
          placement="top"
          :color="getMarketColor(item.market_change_rate)"
          size="large"
        >
          <el-card class="review-card" shadow="hover">
            <div class="review-header">
              <h3>{{ formatDate(item.review_date) }} 市场复盘</h3>
              <div class="review-actions">
                <el-button size="small" type="primary" @click="openDialog(item)">
                  <el-icon><Edit /></el-icon> 编辑
                </el-button>
                <el-popconfirm
                  title="确定删除该复盘记录吗？"
                  @confirm="deleteDailyReview(item.id)"
                >
                  <template #reference>
                    <el-button size="small" type="danger">
                      <el-icon><Delete /></el-icon> 删除
                    </el-button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
            
            <div class="market-data">
              <div class="data-item">
                <span class="label">大盘指数:</span>
                <span class="value">{{ item.market_index }}</span>
              </div>
              <div class="data-item">
                <span class="label">成交金额:</span>
                <span class="value">{{ item.trading_amount }}亿</span>
              </div>
              <div class="data-item">
                <span class="label">涨跌幅:</span>
                <span :class="getMarketRateClass(item.market_change_rate)">{{ item.market_change_rate }}%</span>
              </div>
              <div class="data-item">
                <span class="label">涨停/跌停:</span>
                <span class="value">{{ item.limit_up_count }}/{{ item.limit_down_count }}</span>
              </div>
              <div class="data-item">
                <span class="label">涨/跌家数:</span>
                <span class="value">{{ item.rise_count }}/{{ item.fall_count }}</span>
              </div>
            </div>
            
            <div class="review-content">
              <el-button type="primary" text @click="viewDetail(item)">
                <el-icon><View /></el-icon> 查看详情
              </el-button>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 复盘记录表单对话框 -->
    <el-dialog
      :title="isEdit ? '编辑复盘记录' : '新增复盘记录'"
      v-model="dialogVisible"
      width="800px"
    >
      <el-form :model="form" :rules="rules" ref="dailyReviewForm" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="复盘日期" prop="review_date">
              <el-date-picker
                v-model="form.review_date"
                type="date"
                placeholder="选择复盘日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
              ></el-date-picker>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="大盘指数" prop="market_index">
              <el-input-number
                v-model="form.market_index"
                :precision="2"
                :step="0.01"
                :min="0"
                placeholder="请输入大盘指数"
              ></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="成交金额" prop="trading_amount">
              <el-input-number
                v-model="form.trading_amount"
                :precision="2"
                :step="0.01"
                :min="0"
                placeholder="请输入成交金额(亿元)"
              ></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="涨跌幅" prop="market_change_rate">
              <el-input-number
                v-model="form.market_change_rate"
                :precision="2"
                :step="0.01"
                placeholder="请输入涨跌幅(%)"
              ></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="涨停数" prop="limit_up_count">
              <el-input-number
                v-model="form.limit_up_count"
                :precision="0"
                :step="1"
                :min="0"
                placeholder="请输入涨停数"
              ></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="跌停数" prop="limit_down_count">
              <el-input-number
                v-model="form.limit_down_count"
                :precision="0"
                :step="1"
                :min="0"
                placeholder="请输入跌停数"
              ></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="涨家数" prop="rise_count">
              <el-input-number
                v-model="form.rise_count"
                :precision="0"
                :step="1"
                :min="0"
                placeholder="请输入涨家数"
              ></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="跌家数" prop="fall_count">
              <el-input-number
                v-model="form.fall_count"
                :precision="0"
                :step="1"
                :min="0"
                placeholder="请输入跌家数"
              ></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="复盘内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="10"
            placeholder="请输入复盘内容"
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

    <!-- 详情对话框 -->
    <el-dialog
      title="复盘详情"
      v-model="detailVisible"
      width="800px"
    >
      <div v-if="currentReview" class="detail-container">
        <h2>{{ formatDate(currentReview.review_date) }} 市场复盘</h2>
        
        <div class="market-data-detail">
          <div class="data-item">
            <span class="label">大盘指数:</span>
            <span class="value">{{ currentReview.market_index }}</span>
          </div>
          <div class="data-item">
            <span class="label">成交金额:</span>
            <span class="value">{{ currentReview.trading_amount }}亿</span>
          </div>
          <div class="data-item">
            <span class="label">涨跌幅:</span>
            <span :class="getMarketRateClass(currentReview.market_change_rate)">{{ currentReview.market_change_rate }}%</span>
          </div>
          <div class="data-item">
            <span class="label">涨停/跌停:</span>
            <span class="value">{{ currentReview.limit_up_count }}/{{ currentReview.limit_down_count }}</span>
          </div>
          <div class="data-item">
            <span class="label">涨/跌家数:</span>
            <span class="value">{{ currentReview.rise_count }}/{{ currentReview.fall_count }}</span>
          </div>
        </div>
        
        <div class="content-detail">
          <h3>复盘内容</h3>
          <div class="content-text" v-html="parseMarkdown(currentReview.content)"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, Plus, Edit, Delete, Search, RefreshRight, View } from '@element-plus/icons-vue'
import { marked } from 'marked'
import api from '@/api'

export default {
  name: 'DailyReviews',
  components: {
    Calendar,
    Plus,
    Edit,
    Delete,
    Search,
    RefreshRight,
    View
  },
  setup() {
    const dailyReviews = ref([])
    const loading = ref(false)
    const dialogVisible = ref(false)
    const detailVisible = ref(false)
    const isEdit = ref(false)
    const dailyReviewForm = ref(null)
    const currentReview = ref(null)
    
    const filterForm = reactive({
      dateRange: []
    })
    
    const form = reactive({
      id: '',
      review_date: '',
      market_index: null,
      trading_amount: null,
      market_change_rate: null,
      limit_up_count: null,
      limit_down_count: null,
      rise_count: null,
      fall_count: null,
      content: ''
    })
    
    const rules = {
      review_date: [{ required: true, message: '请选择复盘日期', trigger: 'change' }],
      market_index: [{ required: true, message: '请输入大盘指数', trigger: 'blur' }],
      trading_amount: [{ required: true, message: '请输入成交金额', trigger: 'blur' }],
      market_change_rate: [{ required: true, message: '请输入涨跌幅', trigger: 'blur' }],
      limit_up_count: [{ required: true, message: '请输入涨停数', trigger: 'blur' }],
      limit_down_count: [{ required: true, message: '请输入跌停数', trigger: 'blur' }],
      rise_count: [{ required: true, message: '请输入涨家数', trigger: 'blur' }],
      fall_count: [{ required: true, message: '请输入跌家数', trigger: 'blur' }],
      content: [{ required: true, message: '请输入复盘内容', trigger: 'blur' }]
    }

    /**
     * 获取每日复盘列表
     */
    const fetchDailyReviews = async () => {
      loading.value = true
      try {
        // 构建查询参数
        const params = {}
        if (filterForm.dateRange && filterForm.dateRange.length === 2) {
          params.start_date = filterForm.dateRange[0]
          params.end_date = filterForm.dateRange[1]
        }
        
        const response = await api.get('/daily-reviews/', { params })
        console.log('每日复盘响应:', response)
        dailyReviews.value = response.data || []
      } catch (error) {
        ElMessage.error('获取每日复盘列表失败')
        console.error('获取每日复盘错误:', error)
      } finally {
        loading.value = false
      }
    }

    /**
     * 打开对话框
     * @param {Object} dailyReview - 要编辑的复盘记录对象
     */
    const openDialog = (dailyReview) => {
      resetForm()
      if (dailyReview) {
        isEdit.value = true
        form.id = dailyReview.id
        form.review_date = dailyReview.review_date
        form.market_index = dailyReview.market_index
        form.trading_amount = dailyReview.trading_amount
        form.market_change_rate = dailyReview.market_change_rate
        form.limit_up_count = dailyReview.limit_up_count
        form.limit_down_count = dailyReview.limit_down_count
        form.rise_count = dailyReview.rise_count
        form.fall_count = dailyReview.fall_count
        form.content = dailyReview.content
      } else {
        isEdit.value = false
        // 设置默认模板
        form.content = `# 市场概况

## 市场特征

## 板块分析

## 个股分析

## 总结与展望`
      }
      dialogVisible.value = true
    }

    /**
     * 查看详情
     * @param {Object} dailyReview - 要查看的复盘记录对象
     */
    const viewDetail = (dailyReview) => {
      currentReview.value = dailyReview
      detailVisible.value = true
    }

    /**
     * 重置表单
     */
    const resetForm = () => {
      form.id = ''
      form.review_date = ''
      form.market_index = null
      form.trading_amount = null
      form.market_change_rate = null
      form.limit_up_count = null
      form.limit_down_count = null
      form.rise_count = null
      form.fall_count = null
      form.content = ''
      
      if (dailyReviewForm.value) {
        dailyReviewForm.value.resetFields()
      }
    }

    /**
     * 提交表单
     */
    const submitForm = async () => {
      if (!dailyReviewForm.value) return
      
      await dailyReviewForm.value.validate(async (valid) => {
        if (valid) {
          try {
            const data = {
              review_date: form.review_date,
              market_index: form.market_index,
              trading_amount: form.trading_amount,
              market_change_rate: form.market_change_rate,
              limit_up_count: form.limit_up_count,
              limit_down_count: form.limit_down_count,
              rise_count: form.rise_count,
              fall_count: form.fall_count,
              content: form.content
            }
            
            console.log('提交每日复盘数据:', data)
            
            if (isEdit.value) {
              await api.put(`/daily-reviews/${form.id}`, data)
              ElMessage.success('更新每日复盘成功')
            } else {
              await api.post('/daily-reviews/', data)
              ElMessage.success('创建每日复盘成功')
            }
            dialogVisible.value = false
            fetchDailyReviews()
          } catch (error) {
            ElMessage.error(isEdit.value ? '更新每日复盘失败' : '创建每日复盘失败')
            console.error('提交每日复盘错误:', error)
          }
        }
      })
    }

    /**
     * 删除每日复盘
     * @param {string} id - 每日复盘ID
     */
    const deleteDailyReview = async (id) => {
      try {
        await api.delete(`/daily-reviews/${id}`)
        ElMessage.success('删除每日复盘成功')
        fetchDailyReviews()
      } catch (error) {
        ElMessage.error('删除每日复盘失败')
        console.error(error)
      }
    }

    /**
     * 获取市场涨跌幅样式类
     * @param {number} rate - 涨跌幅
     * @returns {string} 样式类名
     */
    const getMarketRateClass = (rate) => {
      return rate > 0 ? 'profit' : rate < 0 ? 'loss' : ''
    }

    /**
     * 获取时间线点的颜色
     * @param {number} rate - 涨跌幅
     * @returns {string} 颜色
     */
    const getMarketColor = (rate) => {
      return rate > 0 ? '#f56c6c' : rate < 0 ? '#67c23a' : '#409eff'
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

    /**
     * 重置筛选条件
     */
    const resetFilter = () => {
      filterForm.dateRange = []
      fetchDailyReviews()
    }

    /**
     * 解析Markdown内容为HTML
     * @param {string} content - Markdown文本内容
     * @returns {string} HTML格式内容
     */
    const parseMarkdown = (content) => {
      if (!content) return ''
      return marked(content)
    }

    onMounted(() => {
      fetchDailyReviews()
    })

    return {
      dailyReviews,
      loading,
      dialogVisible,
      detailVisible,
      isEdit,
      form,
      rules,
      dailyReviewForm,
      currentReview,
      filterForm,
      openDialog,
      viewDetail,
      submitForm,
      deleteDailyReview,
      getMarketRateClass,
      getMarketColor,
      formatDate,
      resetFilter,
      parseMarkdown
    }
  }
}
</script>

<style scoped>
.daily-reviews-container {
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

.filter-container {
  background-color: white;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.review-card {
  margin-bottom: 16px;
  border-radius: 8px;
  transition: all 0.3s;
}

.review-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.review-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.market-data {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.data-item {
  display: flex;
  align-items: center;
}

.data-item .label {
  font-weight: bold;
  margin-right: 8px;
  color: #606266;
}

.data-item .value {
  color: #303133;
}

.review-content {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

.detail-container {
  padding: 0 20px;
}

.market-data-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.content-detail h3 {
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 12px;
  margin-bottom: 16px;
  color: #303133;
  font-size: 18px;
}

.content-text {
  line-height: 1.8;
  color: #303133;
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

/* Markdown样式 */
.content-text h1 {
  font-size: 24px;
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.content-text h2 {
  font-size: 20px;
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.content-text h3 {
  font-size: 18px;
  margin-top: 20px;
  margin-bottom: 12px;
  font-weight: 600;
  line-height: 1.25;
}

.content-text h4, .content-text h5, .content-text h6 {
  font-weight: 600;
  line-height: 1.25;
  margin-top: 18px;
  margin-bottom: 12px;
}

.content-text p {
  margin-top: 0;
  margin-bottom: 16px;
}

.content-text blockquote {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin: 0 0 16px 0;
}

.content-text ul, .content-text ol {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 16px;
}

.content-text code {
  font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.content-text pre {
  font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
  margin-bottom: 16px;
}

.content-text pre code {
  background-color: transparent;
  padding: 0;
}

.content-text table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
}

.content-text table th, .content-text table td {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.content-text table tr {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.content-text table tr:nth-child(2n) {
  background-color: #f6f8fa;
}

.profit {
  color: #f56c6c;
  font-weight: bold;
}

.loss {
  color: #67c23a;
  font-weight: bold;
}
</style> 