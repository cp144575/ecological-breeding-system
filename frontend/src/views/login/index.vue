<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="title">生态养殖管理系统</h1>
      <el-form :model="login_form" :rules="rules" ref="login_ref" class="login-form">
        <el-form-item prop="username">
          <el-input 
            v-model="login_form.username" 
            placeholder="请输入账号"
            class="custom-input"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="login_form.password" 
            type="password" 
            placeholder="请输入密码" 
            show-password
            class="custom-input"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button 
            class="login-btn btn-standard btn-add" 
            :loading="loading" 
            @click="handle_login"
          >
            登 录
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <span>没有账号？去 </span>
          <router-link to="/register" class="register-link">注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const user_store = useUserStore()
const loading = ref(false)
const login_ref = ref()

const login_form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handle_login = async () => {
  if (!login_ref.value) return
  
  try {
    // 使用 Promise 风格的表单验证
    await login_ref.value.validate()
    
    loading.value = true
    try {
      await user_store.login(login_form)
      ElMessage.success('登录成功')
      router.push('/')
    } catch (error: any) {
      // 登录失败的具体错误已经在 request.ts 的拦截器中通过 ElMessage 处理了
      // 此处仅记录警告日志，不再触发控制台红色错误报告
      console.warn('登录请求失败，错误已在拦截器中处理')
    } finally {
      loading.value = false
    }
  } catch (error) {
    // 表单校验失败，无需处理
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  /* 使用本地背景图，确保加载稳定 */
  background-color: #f0f9eb;
  background-image: linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.2)), 
                    url('/login-bg.jpg');
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;
  position: relative;
}

/* 遮罩层，增加氛围感 */
.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
}

.login-box {
  position: relative;
  z-index: 1;
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.15); /* 降低背景不透明度，从 0.25 降至 0.15 */
  backdrop-filter: blur(5px); /* 降低模糊度，从 15px 降至 5px，使背景更清晰 */
  -webkit-backdrop-filter: blur(5px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
  text-align: center;
}

.title {
  color: #006400; /* 深绿色 */
  font-size: 28px;
  margin-bottom: 30px;
  font-weight: bold;
  letter-spacing: 2px;
}

.login-form {
  margin-top: 20px;
}

/* 自定义输入框样式 */
:deep(.custom-input .el-input__wrapper) {
  background-color: #fff !important;
  border-radius: 4px;
  height: 45px;
  box-shadow: none !important;
}

:deep(.custom-select) {
  width: 100%;
}

:deep(.custom-select .el-input__wrapper) {
  background-color: #fff !important;
  border-radius: 4px;
  height: 45px;
  box-shadow: none !important;
}

.login-btn {
  width: 100%;
  height: 45px;
  background-color: #006400 !important;
  border-color: #006400 !important;
  font-size: 18px;
  font-weight: bold;
  margin-top: 10px;
  transition: all 0.3s;
}

.login-btn:hover {
  background-color: #008000 !important;
  transform: translateY(-2px);
}

.login-footer {
  margin-top: 20px;
  color: #333;
  font-size: 14px;
}

.register-link {
  color: #0000ff;
  text-decoration: none;
  font-weight: bold;
}

.register-link:hover {
  text-decoration: underline;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .login-box {
    width: 90%;
    padding: 20px;
  }
}
</style>
