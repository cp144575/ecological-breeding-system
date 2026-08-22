import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'
import { useCertManageStore } from '@/store/cert_manage'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

/**
 * 路由配置表
 */
const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/register/index.vue')
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', role: 'farmer' }
      },
      {
        path: 'stats',
        name: 'DataStats',
        component: () => import('@/views/stats/index.vue'),
        meta: { title: '数据统计', role: ['farmer', 'admin'] }
      },
      {
        path: 'livestock/category',
        name: 'LivestockCategory',
        component: () => import('@/views/livestock/category.vue'),
        meta: { title: '牲畜分类', role: ['farmer', 'admin'] }
      },
      {
        path: 'livestock/area',
        name: 'LivestockArea',
        component: () => import('@/views/livestock/area.vue'),
        meta: { title: '养殖区域', role: ['farmer', 'admin'] }
      },
      {
        path: 'livestock/batch',
        name: 'LivestockBatch',
        component: () => import('@/views/livestock/batch.vue'),
        meta: { title: '牲畜批次', role: ['farmer', 'admin'] }
      },
      {
        path: 'production/feed',
        name: 'FeedManage',
        component: () => import('@/views/production/feed.vue'),
        meta: { title: '饲料管理', role: ['farmer', 'admin'] }
      },
      {
        path: 'production/feeding',
        name: 'FeedingRecord',
        component: () => import('@/views/production/feeding.vue'),
        meta: { title: '投喂记录', role: ['farmer', 'admin'] }
      },
      {
        path: 'production/vaccination',
        name: 'VaccinationRecord',
        component: () => import('@/views/production/vaccination.vue'),
        meta: { title: '疫苗接种', role: ['farmer', 'admin'] }
      },
      {
        path: 'production/disease',
        name: 'DiseaseReport',
        component: () => import('@/views/production/disease.vue'),
        meta: { title: '疾病上报', role: ['farmer', 'admin', 'vet'] }
      },
      {
        path: 'user/cert',
        name: 'QualificationCert',
        component: () => import('@/views/user/cert.vue'),
        meta: { title: '资格认证', role: 'farmer' }
      },
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/user/profile.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: 'system/users',
        name: 'AccountManage',
        component: () => import('@/views/system/users/index.vue'),
        meta: { title: '账户管理', role: 'admin' }
      },
      {
        path: 'system/trace',
        name: 'TraceManage',
        component: () => import('@/views/system/trace/index.vue'),
        meta: { title: '溯源管理', role: 'admin' }
      },
      {
        path: 'system/cert',
        name: 'CertificationManage',
        component: () => import('@/views/user/cert.vue'),
        meta: { title: '认证管理', role: 'admin' },
        beforeEnter: async (_to, _from, next) => {
          try {
            const user_store = useUserStore()
            if (!user_store.userInfo && user_store.token) {
              await user_store.getUserInfo()
            }
            if (user_store.userInfo?.role === 'admin') {
              const cert_manage_store = useCertManageStore()
              void cert_manage_store.preload_all_tabs()
            }
          } catch {
          }
          next()
        }
      }
    ]
  },
  {
    path: '/public/trace/:code',
    name: 'PublicTrace',
    component: () => import('@/views/trace/index.vue'),
    meta: { title: '溯源信息查询' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

/**
 * 路由守卫：校验 Token
 */
router.beforeEach((to, _from, next) => {
  NProgress.start()
  const token = localStorage.getItem('token')
  const whiteList = ['/login', '/register']
  
  if (whiteList.includes(to.path) || to.path.startsWith('/public/trace/')) {
    next()
  } else {
    if (!token) {
      next('/login')
    } else {
      // 角色权限校验
      const userStore = useUserStore()
      const load_user_info = async () => {
        if (userStore.userInfo) return true
        try {
          await userStore.getUserInfo()
          return true
        } catch {
          userStore.logout()
          return false
        }
      }
      
      load_user_info().then((ok) => {
        if (!ok) {
          next('/login')
          return
        }

        const userRole = userStore.userInfo?.role

        // 处理根路径重定向
        if (to.path === '/') {
          if (userRole === 'admin') {
            next('/stats')
          } else if (userRole === 'vet') {
            next('/production/disease')
          } else {
            next('/dashboard')
          }
          return
        }

        if ((to.meta as any)?.demo_hidden) {
          if (userRole === 'admin') {
            next('/stats')
          } else if (userRole === 'vet') {
            next('/production/disease')
          } else {
            next('/dashboard')
          }
          return
        }

        if (to.meta.role) {
          const role_meta = (to.meta as any).role
          const allowed_roles = Array.isArray(role_meta) ? role_meta : [role_meta]
          if (!allowed_roles.includes(userRole)) {
            if (userRole === 'admin') {
              next('/stats')
            } else if (userRole === 'vet') {
              next('/production/disease')
            } else {
              next('/dashboard')
            }
            return
          }
        }

        next()
      })
    }
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
