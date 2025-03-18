import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import StockTrades from '@/views/StockTrades.vue'
import Categories from '@/views/Categories.vue'
import FailureCases from '@/views/FailureCases.vue'
import DailyReviews from '@/views/DailyReviews.vue'
import DailyFunds from '@/views/DailyFunds.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页' }
  },
  {
    path: '/stock-trades',
    name: 'StockTrades',
    component: StockTrades,
    meta: { title: '交易记录' }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: Categories,
    meta: { title: '分类管理' }
  },
  {
    path: '/failure-cases',
    name: 'FailureCases',
    component: FailureCases,
    meta: { title: '失败案例' }
  },
  {
    path: '/daily-reviews',
    name: 'DailyReviews',
    component: DailyReviews,
    meta: { title: '每日复盘' }
  },
  {
    path: '/daily-funds',
    name: 'DailyFunds',
    component: DailyFunds,
    meta: { title: '资金曲线' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 量化交易管理平台` : '量化交易管理平台'
  next()
})

export default router 