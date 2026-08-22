import { defineStore } from 'pinia'
import request from '@/utils/request'

/**
 * 用户状态管理仓库
 */
export const useUserStore = defineStore('user', {
  state: () => ({
    // 从本地存储获取 Token
    token: localStorage.getItem('token') || '',
    refresh_token: localStorage.getItem('refresh_token') || '',
    // 用户详细信息
    userInfo: null as any,
  }),
  actions: {
    /**
     * 用户登录动作
     * @param loginForm 登录表单数据
     */
    async login(loginForm: any) {
      const res: any = await request.post('/api/users/login/', loginForm)
      this.token = res.access
      localStorage.setItem('token', res.access)
      if (res.refresh) {
        this.refresh_token = res.refresh
        localStorage.setItem('refresh_token', res.refresh)
      }
      await this.getUserInfo()
    },
    /**
     * 获取当前登录用户信息
     */
    async getUserInfo() {
      const res: any = await request.get('/api/users/profile/info/')
      this.userInfo = res
    },
    /**
     * 退出登录，清除状态和本地存储
     */
    logout() {
      this.token = ''
      this.refresh_token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
    }
  }
})
