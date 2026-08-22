<template>
  <div class="register-container">
    <div class="register-box">
      <h1 class="title">账号注册</h1>
      <el-form :model="registerForm" :rules="rules" ref="registerRef" class="register-form">
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
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
            v-model="registerForm.password" 
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

        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码" 
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
            class="register-btn btn-standard btn-add" 
            :loading="loading" 
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form-item>

        <div class="register-footer">
          <span>已有账号？去 </span>
          <router-link to="/login" class="login-link">登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const registerRef = ref()

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const handleRegister = async () => {
  if (!registerRef.value) return
  
  try {
    // 使用 Promise 风格的表单验证
    await registerRef.value.validate()
    
    loading.value = true
    try {
      const payload = {
        username: registerForm.username,
        password: registerForm.password
      }
      await request.post('/api/users/register/', payload)
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } catch (error: any) {
      // 注册失败的具体错误已经在 request.ts 的拦截器中通过 ElMessage 处理了
      // 此处仅记录警告日志，不再触发控制台红色错误报告
      console.warn('注册请求失败，错误已在拦截器中处理')
    } finally {
      loading.value = false
    }
  } catch (error) {
    // 表单校验失败，无需处理
  }
}
</script>

<style scoped>
.register-container {
  height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  /* 使用本地背景图，包含猪、羊等动物元素，确保加载稳定 */
  background-color: #f0f9eb;
  background-image: linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.2)), 
                    url('/register-bg.jpg');
  background-repeat: no-repeat;
  background-position: center;
  background-size: cover;
  position: relative;
}

.register-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
}

.register-box {
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
  color: #006400;
  font-size: 28px;
  margin-bottom: 30px;
  font-weight: bold;
}

.custom-input :deep(.el-input__wrapper) {
  background-color: #fff !important;
  border-radius: 4px;
  height: 45px;
  box-shadow: none !important;
}

.custom-select {
  width: 100%;
}

.custom-select :deep(.el-input__wrapper) {
  background-color: #fff !important;
  border-radius: 4px;
  height: 45px;
  box-shadow: none !important;
}

.register-btn {
  width: 100%;
  height: 45px;
  background-color: #006400 !important;
  border-color: #006400 !important;
  font-size: 18px;
  font-weight: bold;
}

.register-footer {
  margin-top: 20px;
  color: #333;
}

.login-link {
  color: #0000ff;
  text-decoration: none;
  font-weight: bold;
}
</style>
