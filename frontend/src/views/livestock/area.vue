<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>养殖区域管理</h2>
        <el-input
          v-model="query_params.search"
          :placeholder="user_store.userInfo?.role === 'admin' ? '搜索区域名称/描述/养殖户...' : '搜索区域名称/描述...'"
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
      </div>
      <div class="header-right">
        <el-button 
          v-if="user_store.userInfo?.role === 'farmer'"
          class="btn-standard btn-add"
          :disabled="!user_store.userInfo?.profile?.is_verified"
          @click="handle_add"
        >
          <el-icon><Plus /></el-icon>新增区域
        </el-button>
      </div>
    </div>

    <!-- 列表展示区 -->
    <div v-loading="loading" class="area-content">
      <el-row :gutter="20" v-if="area_list.length > 0">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in area_list" :key="item.id" class="mb-4">
          <el-card class="area-card standard-card" :body-style="{ padding: '0px' }" shadow="hover">
            <!-- 卡片头部图片 -->
            <div class="card-image-wrapper">
              <el-image 
                v-if="item.image" 
                :src="item.image" 
                fit="cover" 
                class="card-image"
                :preview-src-list="[item.image]"
                preview-teleported
              />
              <div v-else class="image-placeholder">
                <el-icon class="placeholder-icon"><MapLocation /></el-icon>
              </div>
            </div>

            <!-- 卡片主体 -->
            <div class="card-body">
              <div class="card-title-row">
                <h3 class="area-name" v-html="highlight_text(item.area_name, query_params.search)"></h3>
              </div>
              <p class="area-desc" v-html="highlight_text(item.description || '暂无详细描述...', query_params.search)"></p>
              
              <div class="card-footer">
                <div class="footer-left">
                  <div v-if="user_store.userInfo?.role === 'admin'" class="footer-farmer">
                    <el-icon><User /></el-icon>
                    <span class="footer-farmer-name" v-html="highlight_text(item.farmer_name || '-', query_params.search)"></span>
                  </div>
                </div>
                <div class="table-ops">
                  <!-- 仅养殖户可编辑 -->
                  <el-button 
                    v-if="user_store.userInfo?.role === 'farmer' && user_store.userInfo?.profile?.is_verified"
                    class="btn-action-edit" 
                    link 
                    @click.stop="handle_edit(item)"
                  >
                    <el-icon><Edit /></el-icon>编辑
                  </el-button>
                  
                  <!-- 管理员和已认证养殖户均可删除 -->
                  <el-button 
                    v-if="user_store.userInfo?.role === 'admin' || (user_store.userInfo?.role === 'farmer' && user_store.userInfo?.profile?.is_verified)"
                    class="btn-action-delete" 
                    link 
                    @click.stop="handle_delete(item.id, `确定要删除区域 '${item.area_name}' 吗？`)"
                  >
                    <el-icon><Delete /></el-icon>删除
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty v-else description="暂无养殖区域" />

      <!-- 分页 -->
      <div class="pagination-container" v-if="total > 0">
      <el-pagination
        v-model:current-page="query_params.page"
        :page-size="query_params.page_size"
        layout="total, prev, pager, next"
        :total="total"
        @current-change="handle_page_change"
        background
        size="small"
      />
      </div>
    </div>

    <!-- 弹窗 -->
    <el-dialog 
      :title="is_edit ? '修改区域信息' : '新增养殖区域'" 
      v-model="dialog_visible" 
      width="500px"
      destroy-on-close
      class="custom-dialog"
    >
      <el-form :model="area_form" label-width="100px" ref="form_ref" :rules="rules" label-position="top">
        <el-form-item label="区域名称" prop="area_name">
          <el-input v-model="area_form.area_name" placeholder="请输入区域名称，如：1号牛舍" />
        </el-form-item>
        <el-form-item label="区域图片">
          <el-upload
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handle_image_change"
            accept="image/jpeg,image/png,image/gif"
            :multiple="true"
            :limit="10"
          >
            <el-button class="upload-button" type="primary">
              <el-icon><UploadFilled /></el-icon>
              上传图片
            </el-button>
          </el-upload>
          <div v-if="image_preview" class="preview-container" style="margin-top: 12px;">
            <img :src="image_preview" class="preview-img" />
          </div>
          <p class="form-tip">支持 JPG/JPEG/PNG/GIF，最大5MB</p>
          <el-progress v-if="submit_loading && upload_progress > 0" :percentage="upload_progress" :stroke-width="6" style="margin-top: 8px;" />
        </el-form-item>
        <el-form-item label="区域介绍" prop="description">
          <el-input 
            v-model="area_form.description" 
            type="textarea" 
            :rows="4"
            placeholder="请输入区域的详细介绍..." 
            maxlength="300"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog_visible = false">取消</el-button>
          <el-button class="btn-add" @click="handle_submit" :loading="submit_loading">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：养殖区域管理页面
 * 优化布局为响应式卡片网格，增强视觉美感与操作流畅度
 */
import { ref, onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useCRUD } from '@/hooks/useCRUD'
import { useUserStore } from '@/store/user'
import { Plus, Delete, Edit, User, UploadFilled, MapLocation, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { validate_image_file } from '@/utils/image_upload'

const user_store = useUserStore()

// 使用通用 CRUD Hook
const {
  loading,
  list: area_list,
  total,
  query_params,
  get_list,
  handle_page_change,
  handle_delete,
  highlight_text
} = useCRUD({
  api_url: '/api/livestock/area/',
  refresh_signals: ['area'],
  delete_msg: '确定要删除该区域吗？',
  default_query: {
    page_size: 8
  }
})

const submit_loading = ref(false)
const dialog_visible = ref(false)
const is_edit = ref(false)
const form_ref = ref()
const image_preview = ref('')
const image_file = ref<File | null>(null)
const upload_progress = ref(0)

const revoke_blob_url = (value: unknown) => {
  if (typeof value !== 'string') return
  if (!value.startsWith('blob:')) return
  URL.revokeObjectURL(value)
}

const area_form = reactive({
  id: null,
  area_name: '',
  description: '',
  image: ''
})

const rules = {
  area_name: [{ required: true, message: '请输入区域名称', trigger: 'blur' }]
}

const handle_image_change = (file: any) => {
  void (async () => {
    const raw_file = file?.raw as File | undefined
    if (!raw_file) return

    const result = await validate_image_file(raw_file)
    if (!result.ok) {
      ElMessage({ type: 'error', message: result.error_msg, customClass: 'error-message' })
      return
    }

    revoke_blob_url(image_preview.value)
    image_file.value = raw_file
    image_preview.value = URL.createObjectURL(raw_file)
  })()
}

const handle_add = () => {
  is_edit.value = false
  Object.assign(area_form, { id: null, area_name: '', description: '', image: '' })
  revoke_blob_url(image_preview.value)
  image_preview.value = ''
  image_file.value = null
  dialog_visible.value = true
}

const handle_edit = (row: any) => {
  is_edit.value = true
  Object.assign(area_form, row)
  revoke_blob_url(image_preview.value)
  image_preview.value = String(row?.image || '')
  image_file.value = null
  dialog_visible.value = true
}

const handle_submit = async () => {
  await form_ref.value.validate(async (valid: boolean) => {
    if (valid) {
      submit_loading.value = true
      upload_progress.value = 0
      try {
        const formData = new FormData()
        formData.append('area_name', area_form.area_name)
        formData.append('description', area_form.description || '')
        if (image_file.value) {
          formData.append('image', image_file.value)
        }

        if (is_edit.value) {
          await request.put(`/api/livestock/area/${area_form.id}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (evt: any) => {
              const total = evt?.total
              if (!total) return
              upload_progress.value = Math.min(99, Math.round((evt.loaded / total) * 100))
            }
          })
          ElMessage({ type: 'success', message: '修改成功', customClass: 'success-message' })
        } else {
          await request.post('/api/livestock/area/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (evt: any) => {
              const total = evt?.total
              if (!total) return
              upload_progress.value = Math.min(99, Math.round((evt.loaded / total) * 100))
            }
          })
          ElMessage({ type: 'success', message: '添加成功', customClass: 'success-message' })
        }
        dialog_visible.value = false
        get_list()
      } catch (error: any) {
        if (!error?.response) {
          ElMessage({ type: 'error', message: '上传失败，请重试', customClass: 'error-message' })
          return
        }
        ElMessage({
          type: 'error',
          message: error.response?.data?.detail || error.response?.data?.error || '保存失败',
          customClass: 'error-message'
        })
      } finally {
        upload_progress.value = 0
        submit_loading.value = false
      }
    }
  })
}

onMounted(() => {
  get_list()
})
</script>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 280px;
  transition: all 0.3s;
}

.search-input:focus-within {
  width: 320px;
}

.area-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.area-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.card-image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
  background-color: #f5f7fa;
  overflow: hidden;
}

.card-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  color: #909399;
}

.placeholder-icon {
  font-size: 48px;
  opacity: 0.5;
}

.card-body {
  padding: 20px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.card-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.area-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.area-desc {
  font-size: 14px;
  color: #606266;
  margin: 0 0 20px 0;
  line-height: 1.6;
  height: 44px;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #f2f6fc;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-left {
  display: flex;
  align-items: center;
  min-width: 0;
}

.footer-farmer {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  min-width: 0;
}

.footer-farmer-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 140px;
}

.footer-actions {
  display: flex;
  gap: 8px;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  background: #fff;
}

/* 上传相关 */
.area-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100%;
  height: 180px;
  transition: border-color 0.3s;
}

.area-uploader:hover {
  border-color: #409eff;
}

.uploader-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #909399;
}

.uploader-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.preview-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #fff;
  opacity: 0;
  transition: opacity 0.3s;
}

.preview-container:hover .upload-mask {
  opacity: 1;
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.mr-1 {
  margin-right: 4px;
}

.mb-4 {
  margin-bottom: 16px;
}

.mt-2 {
  margin-top: 8px;
}

@media screen and (max-width: 768px) {
  .area-content {
    margin-top: 12px;
  }
}
</style>
