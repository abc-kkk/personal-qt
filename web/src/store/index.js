import { createStore } from 'vuex'

export default createStore({
  state: {
    categories: [],
    stockTrades: [],
    failureCases: [],
    dailyReviews: [],
    dailyFunds: []
  },
  getters: {
    getCategories: state => state.categories,
    getStockTrades: state => state.stockTrades,
    getFailureCases: state => state.failureCases,
    getDailyReviews: state => state.dailyReviews,
    getDailyFunds: state => state.dailyFunds
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
    },
    SET_DAILY_FUNDS(state, dailyFunds) {
      state.dailyFunds = dailyFunds
    }
  },
  actions: {
    // 这里将添加与API交互的异步操作
  },
  modules: {
    // 可以在这里添加模块化的状态管理
  }
}) 