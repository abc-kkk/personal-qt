import { createStore } from 'vuex'

export default createStore({
  state: {
    categories: [],
    stockTrades: [],
    failureCases: [],
    dailyReviews: []
  },
  getters: {
    getCategories: state => state.categories,
    getStockTrades: state => state.stockTrades,
    getFailureCases: state => state.failureCases,
    getDailyReviews: state => state.dailyReviews
  },
  mutations: {
    SET_CATEGORIES(state, categories) {
      state.categories = categories
    },
    SET_STOCK_TRADES(state, stockTrades) {
      state.stockTrades = stockTrades
    },
    SET_FAILURE_CASES(state, failureCases) {
      state.failureCases = failureCases
    },
    SET_DAILY_REVIEWS(state, dailyReviews) {
      state.dailyReviews = dailyReviews
    }
  },
  actions: {
    // 这里将添加与API交互的异步操作
  },
  modules: {
    // 可以在这里添加模块化的状态管理
  }
}) 