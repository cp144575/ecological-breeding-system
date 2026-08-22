<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>饲料库存管理</h2>
        <el-input
          v-model="query_params.search"
          placeholder="搜索饲料名称"
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
      </div>
      <div class="header-right">
        <el-button 
          v-if="user_store.userInfo?.role !== 'admin'"
          class="btn-standard btn-add"
          :disabled="!user_store.userInfo?.profile?.is_verified"
          @click="handle_add"
        >
          <el-icon><Plus /></el-icon>新增饲料
        </el-button>
      </div>
    </div>

    <!-- 数据列表区 - 响应式卡片布局 -->
    <div v-loading="loading" class="feed-content">
      <el-row :gutter="20" v-if="feed_list.length > 0">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in feed_list" :key="item.id" class="mb-4">
          <el-card class="feed-card standard-card" :body-style="{ padding: '0px' }" shadow="hover">
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
                <el-icon class="placeholder-icon"><Box /></el-icon>
              </div>
              <div class="card-tag-overlay">
                <el-tag :type="item.stock_quantity < 50 ? 'danger' : 'success'" effect="dark">
                  {{ item.stock_quantity }} {{ item.unit }}
                </el-tag>
              </div>
            </div>

            <div class="card-info">
              <div class="card-header-row">
                <h3 class="feed-name" v-html="highlight_text(item.feed_name, query_params.search)"></h3>
                <div class="table-ops">
                  <el-button 
                    v-if="user_store.userInfo?.role !== 'admin'"
                    class="btn-action-edit"
                    link 
                    :disabled="!user_store.userInfo?.profile?.is_verified"
                    @click.stop="handle_edit(item)"
                  >
                    <el-icon><Edit /></el-icon>编辑
                  </el-button>
                  <el-button 
                    class="btn-action-delete"
                    link 
                    :disabled="user_store.userInfo?.role === 'farmer' && !user_store.userInfo?.profile?.is_verified"
                    @click.stop="handle_delete(item.id, `确定要删除饲料 '${item.feed_name}' 吗？`)"
                  >
                    <el-icon><Delete /></el-icon>删除
                  </el-button>
                </div>
              </div>
              
              <p class="feed-desc">{{ item.introduction }}</p>
              
              <div class="card-footer">
                <div class="feed-meta">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ format_date(item.created_at) }}</span>
                </div>
                <div class="farmer-tag" v-if="user_store.userInfo?.role === 'admin'">
                  <el-avatar :size="20" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
                  <span class="farmer-name">{{ item.farmer_name }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-else-if="!loading" description="暂无饲料库存数据" />

      <!-- 分页组件 -->
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

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialog_visible"
      :title="is_edit ? '修改饲料信息' : '添加饲料信息'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="form_ref" label-width="100px" label-position="top">
        <el-form-item label="饲料图片" prop="image">
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

        <el-form-item label="饲料名称" prop="feed_name">
          <el-input v-model="form.feed_name" placeholder="请输入饲料名称" />
        </el-form-item>

        <el-form-item label="饲料简介" prop="introduction">
          <el-input 
            v-model="form.introduction" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入饲料的成分、用途等简介信息" 
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <div style="display: flex; gap: 20px;">
          <el-form-item label="初始库存" prop="stock_quantity" style="flex: 1;">
            <el-input-number v-model="form.stock_quantity" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item label="计量单位" prop="unit" style="flex: 1;">
            <el-input v-model="form.unit" disabled />
          </el-form-item>
        </div>

        <el-form-item label="所属养殖户" prop="farmer" v-if="user_store.userInfo?.role === 'admin'">
          <el-select v-model="form.farmer" placeholder="请选择养殖户" style="width: 100%">
            <el-option
              v-for="item in farmer_list"
              :key="item.id"
              :label="item.farmer_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog_visible = false">取 消</el-button>
          <el-button class="btn-add" @click="submit_form" :loading="submit_loading">
            {{ form.id ? '保 存' : '立 即 创 建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：饲料库存管理页面
 */
import { ref, onMounted, reactive } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Search, Edit, UploadFilled, Box, Calendar } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { useCRUD } from '@/hooks/useCRUD'
import { validate_image_file } from '@/utils/image_upload'

const user_store = useUserStore()
const farmer_list = ref<any[]>([])

// 使用通用 CRUD Hook
const {
  loading,
  list: feed_list,
  total,
  query_params,
  get_list,
  handle_page_change,
  handle_delete,
  highlight_text,
  format_date_time: format_date
} = useCRUD({
  api_url: '/api/production/feed/',
  refresh_signals: ['feedinfo'],
  default_query: {
    page_size: 8
  }
})

// 图片预览与文件
const image_preview = ref('')
const image_file = ref<File | null>(null)
const upload_progress = ref(0)

const revoke_blob_url = (value: unknown) => {
  if (typeof value !== 'string') return
  if (!value.startsWith('blob:')) return
  URL.revokeObjectURL(value)
}

// 弹窗相关
const dialog_visible = ref(false)
const is_edit = ref(false)
const submit_loading = ref(false)
const form_ref = ref()
const form = reactive({
  id: undefined,
  feed_name: '',
  introduction: '',
  stock_quantity: 0,
  unit: 'kg',
  farmer: undefined
})

const rules = {
  feed_name: [{ required: true, message: '请输入饲料名称', trigger: 'blur' }],
  introduction: [{ required: true, message: '请输入饲料简介', trigger: 'blur' }],
  stock_quantity: [{ required: true, message: '请输入库存数量', trigger: 'blur' }],
  unit: [{ required: true, message: '请选择单位', trigger: 'change' }]
}

// 获取养殖户列表 (仅管理员需要)
const get_farmers = async () => {
  if (!user_store.token) return
  try {
    if (!user_store.userInfo) {
      await user_store.getUserInfo()
    }
    if (user_store.userInfo?.role !== 'admin') return
    const res: any = await request.get('/api/users/farmer/')
    farmer_list.value = res.results || res
  } catch (error) {
    console.error(error)
  }
}

// 图片选择回调
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

// 打开添加弹窗
const handle_add = () => {
  is_edit.value = false
  Object.assign(form, {
    id: undefined,
    feed_name: '',
    introduction: '',
    stock_quantity: 0,
    unit: 'kg',
    farmer: undefined
  })
  revoke_blob_url(image_preview.value)
  image_preview.value = ''
  image_file.value = null
  dialog_visible.value = true
}

// 打开编辑弹窗
const handle_edit = (row: any) => {
  is_edit.value = true
  Object.assign(form, row)
  revoke_blob_url(image_preview.value)
  image_preview.value = String(row?.image || '')
  image_file.value = null
  dialog_visible.value = true
}

// 提交表单
const submit_form = async () => {
  if (!form_ref.value) return
  await form_ref.value.validate(async (valid: boolean) => {
    if (valid) {
      submit_loading.value = true
      upload_progress.value = 0
      try {
        const formData = new FormData()
        formData.append('feed_name', form.feed_name)
        formData.append('introduction', form.introduction)
        formData.append('stock_quantity', String(form.stock_quantity))
        formData.append('unit', form.unit)
        if (image_file.value) {
          formData.append('image', image_file.value)
        }

        if (is_edit.value) {
          await request.put(`/api/production/feed/${form.id}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (evt: any) => {
              const total = evt?.total
              if (!total) return
              upload_progress.value = Math.min(99, Math.round((evt.loaded / total) * 100))
            }
          })
          ElMessage({ type: 'success', message: '修改成功', customClass: 'success-message' })
        } else {
          await request.post('/api/production/feed/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (evt: any) => {
              const total = evt?.total
              if (!total) return
              upload_progress.value = Math.min(99, Math.round((evt.loaded / total) * 100))
            }
          })
          ElMessage({ type: 'success', message: '入库成功', customClass: 'success-message' })
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
          message: error.response?.data?.detail || error.response?.data?.error || '操作失败',
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
  get_farmers()
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

.feed-content {
  margin-top: 20px;
}

/* 饲料卡片样式 */
.feed-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
}

.feed-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.card-image-wrapper {
  height: 200px;
  background-color: #f5f7fa;
  position: relative;
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  transition: transform 0.5s;
}

.feed-card:hover .card-image {
  transform: scale(1.05);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

.placeholder-icon {
  font-size: 48px;
  color: #909399;
}

.card-tag-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1;
}

.card-info {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.feed-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.feed-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0 0 20px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.card-footer {
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feed-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}

.farmer-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: #f5f7fa;
  padding: 4px 8px;
  border-radius: 12px;
}

.farmer-name {
  font-size: 12px;
  color: #606266;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  background: #fff;
}

.mb-4 {
  margin-bottom: 20px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .page-container {
    padding: 12px;
  }

  .header-section {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .search-input {
    width: 100% !important;
  }

  .header-actions .el-button {
    width: 100%;
    margin-left: 0 !important;
  }

  .feed-content {
    margin-top: 12px;
  }

  .card-image-wrapper {
    height: 160px;
  }
}

/* 弹窗与上传 */
.feed-uploader {
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 120px;
  height: 120px;
  transition: all 0.3s;
}

.feed-uploader:hover {
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
  background: rgba(0, 0, 0, 0.5);
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

@media screen and (max-width: 768px) {
  .feed-content {
    margin-top: 12px;
  }
}
</style>
