<template>
  <div class="home-container">
    <div class="welcome-section">
      <h1>个人量化交易管理平台</h1>
      <p>记录、分析、提升您的交易表现</p>
    </div>
    
    <el-row :gutter="24">
      <el-col :span="8">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-title"><el-icon><Histogram /></el-icon> 交易记录</span>
              <el-button class="button" type="primary" text @click="$router.push('/stock-trades')">查看更多</el-button>
            </div>
          </template>
          <div class="card-content">
            <el-empty v-if="!stockTrades.length" description="暂无交易记录"></el-empty>
            <div v-else>
              <div v-for="(trade, index) in stockTrades.slice(0, 5)" :key="index" class="list-item trade-item">
                <div class="item-main">
                  <div class="item-title">{{ trade.stock_name }} <span class="stock-code">({{ trade.stock_code }})</span></div>
                  <div class="item-date">{{ formatDate(trade.buy_date) }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-title"><el-icon><Warning /></el-icon> 失败案例</span>
              <el-button class="button" type="primary" text @click="$router.push('/failure-cases')">查看更多</el-button>
            </div>
          </template>
          <div class="card-content">
            <el-empty v-if="!failureCases.length" description="暂无失败案例"></el-empty>
            <div v-else>
              <div v-for="(failureCase, index) in failureCases.slice(0, 5)" :key="index" class="list-item failure-item">
                <div class="item-main">
                  <div class="item-title">{{ failureCase.stock_name }} <span class="stock-code">({{ failureCase.stock_code }})</span></div>
                  <div class="item-reason">{{ truncateText(failureCase.reason, 30) }}</div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="header-title"><el-icon><Calendar /></el-icon> 每日复盘</span>
              <el-button class="button" type="primary" text @click="$router.push('/daily-reviews')">查看更多</el-button>
            </div>
          </template>
          <div class="card-content">
            <el-empty v-if="!dailyReviews.length" description="暂无复盘记录"></el-empty>
            <div v-else>
              <div v-for="(review, index) in dailyReviews.slice(0, 5)" :key="index" class="list-item review-item">
                <div class="item-main">
                  <div class="item-title">{{ formatDate(review.review_date) }}</div>
                  <div class="item-rate" :class="getMarketRateClass(review.market_change_rate)">
                    涨跌幅: {{ review.market_change_rate }}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Calendar, Histogram, Warning } from '@element-plus/icons-vue'
import api from '@/api'

export default {
  name: 'Home',
  components: {
    Calendar,
    Histogram,
    Warning
  },
  setup() {
    const stockTrades = ref([])
    const failureCases = ref([])
    const dailyReviews = ref([])

    /**
     * 获取首页数据
     */
    const fetchData = async () => {
      try {
        // 获取最新的5条交易记录
        const tradesResponse = await api.get('/stock-trades/', { params: { limit: 5 } })
        console.log('首页交易记录响应:', tradesResponse)
        stockTrades.value = tradesResponse.data || []
        
        // 获取最新的5条失败案例
        const failuresResponse = await api.get('/failure-cases/', { params: { limit: 5 } })
        console.log('首页失败案例响应:', failuresResponse)
        failureCases.value = failuresResponse.data || []
        
        // 获取最新的5条每日复盘
        const reviewsResponse = await api.get('/daily-reviews/', { params: { limit: 5 } })
        console.log('首页每日复盘响应:', reviewsResponse)
        dailyReviews.value = reviewsResponse.data || []
      } catch (error) {
        console.error('获取首页数据失败', error)
      }
    }

    /**
     * 格式化日期
     */
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    /**
     * 截断文本
     */
    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    /**
     * 获取市场涨跌幅样式类
     */
    const getMarketRateClass = (rate) => {
      return rate > 0 ? 'profit' : rate < 0 ? 'loss' : ''
    }

    onMounted(() => {
      fetchData()
    })

    return {
      stockTrades,
      failureCases,
      dailyReviews,
      formatDate,
      truncateText,
      getMarketRateClass
    }
  }
}
</script>

<style scoped>
.home-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.welcome-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 30px 0;
  background: linear-gradient(135deg, #1976d2, #64b5f6);
  color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.welcome-section h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

.welcome-section p {
  font-size: 16px;
  opacity: 0.9;
}

.box-card {
  height: 100%;
  margin-bottom: 24px;
  border-radius: 8px;
  transition: all 0.3s;
}

.box-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: bold;
  display: flex;
  align-items: center;
}

.header-title .el-icon {
  margin-right: 8px;
}

.card-content {
  min-height: 280px;
  padding: 8px 0;
}

.list-item {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  transition: all 0.2s;
  border-bottom: 1px solid #ebeef5;
}

.list-item:hover {
  background-color: #f5f7fa;
}

.list-item:last-child {
  border-bottom: none;
}

.item-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.item-title {
  font-weight: bold;
  color: #303133;
}

.stock-code {
  color: #909399;
  font-weight: normal;
  font-size: 0.9em;
}

.item-date, .item-reason {
  color: #606266;
  font-size: 0.9em;
}

.item-rate {
  font-weight: bold;
}

.profit {
  color: #f56c6c;
}

.loss {
  color: #67c23a;
}
</style> 