<template>
  <el-container class="layout-container">
    <!-- 侧边导航栏 -->
    <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar-aside">
      <div class="logo-container">
        <el-icon size="24" color="#fff"><Opportunity /></el-icon>
        <span v-show="!isCollapse" class="logo-text">生态养殖系统</span>
      </div>
      
      <el-scrollbar>
        <el-menu
          router
          :default-active="$route.path"
          class="el-menu-vertical"
          :collapse="isCollapse"
          background-color="transparent"
          text-color="#bfcbd9"
          active-text-color="#ffffff"
        >
          <el-menu-item index="/dashboard" v-if="user_store.userInfo?.role === 'farmer'">
            <el-icon><HomeFilled /></el-icon>
            <span>系统首页</span>
          </el-menu-item>

          <el-menu-item index="/stats" v-if="user_store.userInfo?.role !== 'vet'">
            <el-icon><Histogram /></el-icon>
            <span>数据统计</span>
          </el-menu-item>

          <el-sub-menu index="livestock" v-if="user_store.userInfo?.role !== 'vet'">
            <template #title>
              <el-icon><Management /></el-icon>
              <span>牲畜管理</span>
            </template>
            <el-menu-item index="/livestock/area">养殖区域</el-menu-item>
            <el-menu-item index="/livestock/batch">牲畜批次</el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="production">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>生产防疫</span>
            </template>
            <el-menu-item index="/production/feed" v-if="user_store.userInfo?.role !== 'vet'">饲料管理</el-menu-item>
            <el-menu-item index="/production/feeding" v-if="user_store.userInfo?.role !== 'vet'">投喂记录</el-menu-item>
            <el-menu-item index="/production/vaccination" v-if="user_store.userInfo?.role !== 'vet'">疫苗接种</el-menu-item>
            <el-menu-item index="/production/disease">疾病上报</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/user/cert" v-if="user_store.userInfo?.role === 'farmer'">
            <el-icon><Postcard /></el-icon>
            <span>资格认证</span>
          </el-menu-item>

          <el-sub-menu index="system" v-if="user_store.userInfo?.role === 'admin'">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/system/cert">认证管理</el-menu-item>
            <el-menu-item index="/system/trace">溯源管理</el-menu-item>
            <el-menu-item index="/system/users">账户管理</el-menu-item>
          </el-sub-menu>

        </el-menu>
      </el-scrollbar>
    </el-aside>

    <el-container class="main-container">
      <!-- 顶部状态栏 -->
      <el-header class="layout-header">
        <div class="header-left">
          <div class="collapse-btn" @click="isCollapse = !isCollapse">
            <el-icon size="20">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </div>
          <el-breadcrumb separator="/" class="hidden-on-mobile">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="$route.meta.title">{{ $route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-space :size="20">
            <el-dropdown @command="handle_command" trigger="click">
              <div class="user-profile">
                <el-avatar :size="32" :src="avatar_url">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <span class="username">{{ user_store.userInfo?.username }}</span>
                <el-icon><arrow-down /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>个人中心
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-space>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
/**
 * 页面主体布局组件
 * 包含侧边导航栏、顶部状态栏及主内容区域
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { useRouter } from 'vue-router'
import {
  HomeFilled, Histogram, Management, Box,
  Postcard, Fold, Expand,
  User, SwitchButton, Opportunity, ArrowDown, Setting
} from '@element-plus/icons-vue'

const user_store = useUserStore()
const router = useRouter()
const isCollapse = ref(false)
const screenWidth = ref(window.innerWidth)

const handleResize = () => {
  screenWidth.value = window.innerWidth
  if (screenWidth.value <= 768) {
    isCollapse.value = true
  } else {
    isCollapse.value = false
  }
}

// 计算头像 URL
const avatar_url = computed(() => {
  const avatar = user_store.userInfo?.avatar
  if (avatar) {
    if (avatar.startsWith('http')) return avatar
    return avatar
  }
  return ''
})

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  handleResize() // 初始化执行一次
  
  if (!user_store.userInfo && user_store.token) {
    try {
      await user_store.getUserInfo()
    } catch (error) {
      console.error('获取用户信息失败', error)
      router.push('/login')
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

/**
 * 处理顶部下拉菜单命令
 */
const handle_command = (command: string) => {
  if (command === 'logout') {
    user_store.logout()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar-aside {
  background-color: #1a2f23; /* 深邃生态绿背景 */
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  z-index: 1001;
  box-shadow: 4px 0 10px rgba(0, 0, 0, 0.1);
}

.logo-container {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #14251c;
  overflow: hidden;
  white-space: nowrap;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo-text {
  margin-left: 12px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
  background: linear-gradient(to right, #fff, #a5d6a7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.el-menu-vertical {
  border-right: none;
  padding: 10px 0;
}

.el-menu-vertical :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.el-menu-vertical :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, var(--primary-green), var(--secondary-green)) !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(45, 138, 78, 0.3);
}

.el-menu-vertical :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: #fff !important;
}

.el-menu-vertical :deep(.el-sub-menu__title) {
  margin: 4px 12px;
  border-radius: 8px;
}

.el-menu-vertical :deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: #fff !important;
}

/* 顶部状态栏样式 */
.layout-header {
  background: var(--bg-header-gradient) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-sm);
  border-bottom: 1px solid var(--border-header);
  z-index: 1000;
  height: 64px !important;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background-color: var(--light-green);
  color: var(--primary-green);
  transform: scale(1.05);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  transition: var(--transition-base);
  border: 1px solid transparent;
}

.user-profile:hover {
  background-color: #ffffff;
  border-color: var(--border-color);
  box-shadow: var(--shadow-subtle);
}

.username {
  margin: 0 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-dark);
}

/* 主内容区域样式 */
.layout-main {
  background-image: var(--bg-main-gradient), var(--bg-main-pattern);
  background-size: 100% 100%, 20px 20px;
  background-attachment: fixed;
  padding: 24px;
  overflow-y: auto;
  position: relative;
}

.layout-main::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.02), transparent);
  pointer-events: none;
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .layout-main {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .hidden-on-mobile {
    display: none;
  }
  
  .sidebar-aside {
    position: fixed;
    height: 100vh;
  }

  .main-container {
    margin-left: 0;
  }
}
</style>
