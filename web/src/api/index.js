import axios from 'axios'

const api = axios.create({
  // 使用环境变量中配置的API基础URL
  baseURL: import.meta.env.VITE_API_BASE_URL,
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