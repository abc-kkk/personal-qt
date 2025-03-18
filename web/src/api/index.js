import axios from 'axios'

// 根据环境判断是否是生产环境
const isProd = process.env.NODE_ENV === 'production'

const api = axios.create({
  // 生产环境使用相对路径，开发环境使用本地服务器
  baseURL: isProd ? '' : 'http://8.138.205.53:8000/',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('发送请求:', config.url, config.params || config.data)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('接收响应:', response.config.url, response.data)
    return response
  },
  error => {
    // 处理错误响应
    if (error.response) {
      // 服务器返回错误状态码
      console.error('API错误:', error.response.data)
    } else if (error.request) {
      // 请求发送但没有收到响应
      console.error('网络错误:', error.request)
    } else {
      // 请求设置时发生错误
      console.error('请求错误:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api 