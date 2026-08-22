import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/',
  timeout: 5000
})

const refresh_client = axios.create({
  baseURL: '/',
  timeout: 5000
})

let is_refreshing = false
let refresh_waiters: Array<(token: string) => void> = []

const notify_refreshed = (token: string) => {
  refresh_waiters.forEach((cb) => cb(token))
  refresh_waiters = []
}

const wait_for_refresh = () =>
  new Promise<string>((resolve) => {
    refresh_waiters.push(resolve)
  })

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  async error => {
    let message = '网络错误'
    const data = error.response?.data
    
    if (data) {
      if (typeof data === 'string') {
        message = data
      } else if (data.detail || data.error) {
        message = data.detail || data.error
      } else if (typeof data === 'object') {
        // 处理 Django REST Framework 的字段验证错误，例如 {"username": ["已存在"]}
        const firstKey = Object.keys(data)[0]
        if (firstKey) {
          const firstError = (data as any)[firstKey]
          if (Array.isArray(firstError)) {
            message = `${firstKey}: ${firstError[0]}`
          } else if (typeof firstError === 'string') {
            message = firstError
          }
        }
      }
    }
    
    // 针对 401：登录失败提示 or access 过期自动刷新
    if (error.response?.status === 401) {
      // 检查是否在登录页面（兼容有无斜杠的情况）
      const isLoginPage = window.location.pathname === '/login' || window.location.pathname === '/login/'
      
      if (isLoginPage) {
        const detail = error.response?.data?.detail
        if (detail === 'No active account found with the given credentials') {
          message = '账号或密码错误，请重新输入'
        } else if (typeof detail === 'string' && detail) {
          message = detail
        } else {
          message = '账号或密码错误，请重新输入'
        }
      } else {
        const original_config: any = error.config || {}
        const request_url = String(original_config?.url || '')
        const refresh_token = localStorage.getItem('refresh_token') || ''
        const is_refresh_request = request_url.includes('/api/users/token/refresh/')
        const is_login_request = request_url.includes('/api/users/login/')
        const already_retried = Boolean(original_config?._retry)

        if (refresh_token && !is_refresh_request && !is_login_request && !already_retried) {
          original_config._retry = true

          try {
            if (!is_refreshing) {
              is_refreshing = true
              const refresh_response: any = await refresh_client.post('/api/users/token/refresh/', {
                refresh: refresh_token
              })
              const new_access = refresh_response?.data?.access
              if (!new_access) {
                throw new Error('no access token')
              }
              localStorage.setItem('token', new_access)
              notify_refreshed(new_access)
              is_refreshing = false
            } else {
              const new_access = await wait_for_refresh()
              localStorage.setItem('token', new_access)
            }

            const latest_access = localStorage.getItem('token') || ''
            original_config.headers = original_config.headers || {}
            original_config.headers['Authorization'] = `Bearer ${latest_access}`
            return service(original_config)
          } catch (_refresh_error) {
            is_refreshing = false
            refresh_waiters = []
            message = '登录已过期，请重新登录'
            localStorage.removeItem('token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
          }
        } else {
          message = '登录已过期，请重新登录'
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    
    // 确保消息不为空
    const finalMessage = message || '未知错误'
    console.error('请求错误:', {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: finalMessage
    })
    ElMessage.error(finalMessage)
    return Promise.reject(error)
  }
)

export default service
