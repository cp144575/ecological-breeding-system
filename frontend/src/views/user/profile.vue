<template>
  <div class="page-container profile-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>个人资料设置</h2>
      </div>
    </div>

    <el-row :gutter="24">
      <!-- 左侧：基本信息 -->
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="user-info-card standard-card" shadow="hover">
          <div class="avatar-section">
            <div class="avatar-wrapper" @click="open_upload">
              <el-avatar :size="120" :src="avatar_url">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="avatar-hover">
                <el-icon><Camera /></el-icon>
                <span>更换头像</span>
              </div>
            </div>
            <h2 class="username">{{ user_store.userInfo?.username }}</h2>
            <el-tag
              :type="user_store.userInfo?.role === 'admin' ? 'danger' : (user_store.userInfo?.role === 'vet' ? 'warning' : 'success')"
              effect="plain"
            >
              {{ user_store.userInfo?.role === 'admin' ? '系统管理员' : (user_store.userInfo?.role === 'vet' ? '兽医' : '养殖户') }}
            </el-tag>
          </div>
          
          <div class="detail-section">
            <div class="detail-item">
              <el-icon class="mr-1"><Phone /></el-icon>
              <span class="label">手机号：</span>
              <span class="value">{{ user_store.userInfo?.phone || '未绑定' }}</span>
            </div>
            <div class="detail-item">
              <el-icon class="mr-1"><Calendar /></el-icon>
              <span class="label">注册时间：</span>
              <span class="value">{{ format_date(user_store.userInfo?.date_joined) }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：操作区域 -->
      <el-col :xs="24" :sm="24" :md="16">
        <el-card class="standard-card settings-card" shadow="hover">
          <el-tabs v-model="active_tab" class="profile-tabs">
            <el-tab-pane label="基本资料" name="info">
              <el-form :model="info_form" label-width="100px" class="profile-form" label-position="top">
                <el-form-item label="用户名">
                  <el-input v-model="info_form.username" disabled />
                </el-form-item>
                <el-form-item label="手机号">
                  <el-input v-model="info_form.phone" placeholder="请输入手机号" maxlength="11" />
                </el-form-item>
                <div class="form-actions table-ops">
                  <el-button class="btn-standard btn-add" @click="handle_update_info">保存修改</el-button>
                </div>
              </el-form>
            </el-tab-pane>
            
            <el-tab-pane label="安全设置" name="password">
              <el-form :model="pwd_form" :rules="pwd_rules" ref="pwd_ref" label-width="100px" class="profile-form" label-position="top">
                <el-form-item label="原密码" prop="old_password">
                  <el-input v-model="pwd_form.old_password" type="password" show-password placeholder="请输入原密码" />
                </el-form-item>
                <el-form-item label="新密码" prop="new_password">
                  <el-input v-model="pwd_form.new_password" type="password" show-password placeholder="请输入新密码" />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirm_password">
                  <el-input v-model="pwd_form.confirm_password" type="password" show-password placeholder="请再次输入新密码" />
                </el-form-item>
                <div class="form-actions table-ops">
                  <el-button class="btn-standard btn-add" @click="handle_update_pwd">修改密码</el-button>
                  <el-button @click="reset_pwd_form">重置</el-button>
                </div>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 头像上传对话框 -->
    <el-dialog
      v-model="upload_dialog.visible"
      title="更换头像"
      width="400px"
      @closed="handle_upload_closed"
    >
      <div class="upload-dialog-content">
        <el-upload
          action="#"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handle_file_change"
          accept="image/jpeg,image/png,image/gif"
          :multiple="true"
          :limit="10"
        >
          <el-button class="upload-button" type="primary">
            <el-icon><UploadFilled /></el-icon>
            上传图片
          </el-button>
        </el-upload>
        <div v-if="upload_dialog.preview_url" style="margin-top: 12px;">
          <img :src="upload_dialog.preview_url" class="avatar-preview" />
        </div>
        <div class="upload-tip">支持 JPG/JPEG/PNG/GIF，最大5MB</div>
        <el-progress v-if="upload_dialog.loading && upload_dialog.progress > 0" :percentage="upload_dialog.progress" :stroke-width="6" style="margin-top: 8px;" />
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="upload_dialog.visible = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="upload_dialog.loading"
            :disabled="!upload_dialog.file"
            @click="handle_confirm_upload"
          >
            确认上传
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：个人中心页面
 * 提供基本信息展示及账号安全设置，支持头像上传
 */
import { ref, reactive, onMounted, computed } from 'vue'
import { useUserStore } from '@/store/user'
import { User, Phone, Calendar, Camera, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { format_date } from '@/hooks/useCRUD'
import request from '@/utils/request'
import { validate_image_file } from '@/utils/image_upload'

const user_store = useUserStore()
const active_tab = ref('info')
const pwd_ref = ref()

// 计算头像 URL
const avatar_url = computed(() => {
  const avatar = user_store.userInfo?.avatar
  if (avatar) {
    if (avatar.startsWith('http')) return avatar
    return avatar
  }
  return ''
})

const upload_dialog = reactive({
  visible: false,
  loading: false,
  file: null as File | null,
  preview_url: '',
  progress: 0
})

const open_upload = () => {
  upload_dialog.visible = true
}

const handle_file_change = (uploadFile: any) => {
  void (async () => {
    const file = uploadFile?.raw as File | undefined
    if (!file) return

    const result = await validate_image_file(file)
    if (!result.ok) {
      ElMessage({ type: 'error', message: result.error_msg, customClass: 'error-message' })
      return
    }

    if (upload_dialog.preview_url && upload_dialog.preview_url.startsWith('blob:')) {
      URL.revokeObjectURL(upload_dialog.preview_url)
    }

    upload_dialog.file = file
    upload_dialog.preview_url = URL.createObjectURL(file)
  })()
}

const handle_confirm_upload = async () => {
  if (!upload_dialog.file) return
  
  upload_dialog.loading = true
  upload_dialog.progress = 0
  const formData = new FormData()
  formData.append('avatar', upload_dialog.file)
  
  try {
    await request.post('/api/users/profile/upload_avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (evt: any) => {
        const total = evt?.total
        if (!total) return
        upload_dialog.progress = Math.min(99, Math.round((evt.loaded / total) * 100))
      }
    })
    ElMessage({ type: 'success', message: '头像上传成功', customClass: 'success-message' })
    upload_dialog.visible = false
    // 更新本地用户信息
    await user_store.getUserInfo()
  } catch (error: any) {
    if (!error?.response) {
      ElMessage({ type: 'error', message: '上传失败，请重试', customClass: 'error-message' })
      return
    }
    ElMessage({
      type: 'error',
      message: error.response?.data?.detail || error.response?.data?.error || '上传失败，请重试',
      customClass: 'error-message'
    })
  } finally {
    upload_dialog.loading = false
    upload_dialog.progress = 0
  }
}

const handle_upload_closed = () => {
  upload_dialog.file = null
  if (upload_dialog.preview_url) {
    URL.revokeObjectURL(upload_dialog.preview_url)
    upload_dialog.preview_url = ''
  }
  upload_dialog.progress = 0
}

const info_form = reactive({
  username: '',
  phone: ''
})

const pwd_form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const pwd_rules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: any, callback: any) => {
        if (value !== pwd_form.new_password) {
          callback(new Error('两次输入密码不一致!'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

onMounted(() => {
  if (user_store.userInfo) {
    info_form.username = user_store.userInfo.username
    info_form.phone = user_store.userInfo.phone
  }
})

const handle_update_info = async () => {
  try {
    await request.patch('/api/users/profile/update_info/', {
      phone: info_form.phone
    })
    ElMessage.success('个人信息更新成功')
    await user_store.getUserInfo()
  } catch (error) {
    console.error('更新信息失败', error)
  }
}

const handle_update_pwd = async () => {
  if (!pwd_ref.value) return
  await pwd_ref.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await request.post('/api/users/profile/change_password/', {
          old_password: pwd_form.old_password,
          new_password: pwd_form.new_password
        })
        ElMessage.success('密码修改成功，请重新登录')
        user_store.logout()
        window.location.reload()
      } catch (error) {
        console.error('修改密码失败', error)
      }
    }
  })
}

const reset_pwd_form = () => {
  pwd_ref.value?.resetFields()
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 24px;
}

.header-title h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.standard-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  height: 100%;
}

.user-info-card {
  text-align: center;
  padding: 20px 0;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
  margin-bottom: 16px;
  border-radius: 50%;
  overflow: hidden;
  transition: all 0.3s;
}

.avatar-hover {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 14px;
}

.avatar-wrapper:hover .avatar-hover {
  opacity: 1;
}

.username {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

.detail-section {
  text-align: left;
  padding: 0 20px;
  border-top: 1px solid #f0f2f5;
  padding-top: 24px;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
  color: #606266;
}

.detail-item .el-icon {
  margin-right: 12px;
  font-size: 18px;
  color: #909399;
}

.detail-item .label {
  color: #909399;
}

.detail-item .value {
  color: #303133;
}

.settings-card :deep(.el-card__body) {
  padding: 0;
}

.profile-tabs :deep(.el-tabs__header) {
  padding: 0 24px;
  margin: 0;
}

.profile-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

.profile-form {
  padding: 32px 24px;
  max-width: 600px;
}

.form-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f2f5;
}

.upload-dialog-content {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 178px;
  height: 178px;
  transition: border-color 0.3s;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.preview-container {
  width: 178px;
  height: 178px;
  position: relative;
}

.avatar-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.preview-container:hover .preview-mask {
  opacity: 1;
}

.mr-1 {
  margin-right: 4px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .user-info-card {
    margin-bottom: 24px;
  }

  .profile-form {
    padding: 20px 16px;
  }
}
</style>
