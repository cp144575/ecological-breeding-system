<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>大类模板管理</h2>
        <el-input
          v-model="query_params.search"
          placeholder="搜索大类名称或代码..."
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
      </div>
      <div class="header-right" />
    </div>

    <el-alert
      v-if="user_store.userInfo?.role === 'admin'"
      type="info"
      show-icon
      :closable="false"
      title="系统内置六大类：不支持新增/删除/改名/改码，仅可维护图标、描述与标准生长周期。"
      style="margin-bottom: 16px;"
    />

    <!-- 数据列表区 - 改为响应式卡片布局 -->
    <div v-loading="loading" class="category-content">
      <el-row :gutter="20" v-if="category_list.length > 0">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in category_list" :key="item.id" class="mb-4">
          <el-card class="category-card standard-card" :body-style="{ padding: '0px' }" shadow="hover">
            <!-- 卡片头部图标/占位 -->
            <div class="card-image-wrapper">
              <div class="category-icon-placeholder">
                <el-image v-if="item.icon" :src="item.icon" class="category-icon-img" />
                <el-icon v-else class="placeholder-icon"><Collection /></el-icon>
              </div>
              <div class="card-tag-overlay">
                <el-tag size="small" effect="dark" type="success">{{ item.category_code || 'STANDARD' }}</el-tag>
              </div>
            </div>

            <div class="card-info">
              <div class="card-header-row">
                <h3 class="category-name" v-html="highlight_text(item.name, query_params.search)"></h3>
                <div class="table-ops" v-if="user_store.userInfo?.role === 'admin'">
                  <el-button class="btn-action-edit" link @click.stop="handle_edit(item)">
                    <el-icon><Edit /></el-icon>编辑
                  </el-button>
                </div>
              </div>
              
              <div class="cycle-info">
                <el-icon><Timer /></el-icon>
                <span>标准生长周期: <strong>{{ item.standard_cycle }}</strong> 天</span>
              </div>
              
              <p class="category-desc" v-html="highlight_text(item.description || '暂无详细描述信息', query_params.search)"></p>
              
              <div class="card-footer">
                <div class="category-meta">
                  <el-icon><InfoFilled /></el-icon>
                  <span>点击查看详情</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-else-if="!loading" description="暂无分类数据" />

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

    <el-dialog
      v-model="dialog_visible"
      title="修改大类信息"
      width="500px"
      destroy-on-close
      class="custom-dialog"
    >
      <el-form :model="form" :rules="rules" ref="form_ref" label-width="100px" label-position="top">
        <el-row :gutter="20">
            <el-col :span="14">
              <el-form-item label="大类名称" prop="name">
                <el-input 
                  v-model="form.name" 
                  placeholder="如：鸡、鸭、猪等" 
                  maxlength="20"
                  show-word-limit
                  :disabled="is_edit"
                />
              </el-form-item>
            </el-col>
            <el-col :span="10">
              <el-form-item label="分类代码" prop="category_code">
                <el-input v-model="form.category_code" placeholder="如：POULTRY" :disabled="is_edit" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="分类图标" prop="icon">
            <el-upload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handle_icon_change"
              accept="image/jpeg,image/png,image/gif"
              :multiple="true"
              :limit="10"
            >
              <el-button class="upload-button" type="primary">
                <el-icon><UploadFilled /></el-icon>
                上传图片
              </el-button>
            </el-upload>
            <div v-if="preview_url" style="margin-top: 12px;">
              <img :src="preview_url" class="preview-img" />
            </div>
            <p class="form-tip">支持 JPG/JPEG/PNG/GIF，最大5MB</p>
            <el-progress v-if="submit_loading && upload_progress > 0" :percentage="upload_progress" :stroke-width="6" style="margin-top: 8px;" />
          </el-form-item>

          <el-form-item label="标准生长周期 (天)" prop="standard_cycle">
          <el-input-number v-model="form.standard_cycle" :min="0" style="width: 100%" />
          <p class="form-tip">用于出栏预警提醒。</p>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="3" 
            placeholder="简要说明该大类的养殖标准..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog_visible = false">取消</el-button>
          <el-button class="btn-add" @click="handle_submit" :loading="submit_loading">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { Edit, UploadFilled, Collection, InfoFilled, Timer, Search } from '@element-plus/icons-vue'
import { useCRUD } from '@/hooks/useCRUD'
import { validate_image_file } from '@/utils/image_upload'

const user_store = useUserStore()

// 使用通用 CRUD Hook
const {
  loading,
  list: category_list,
  total,
  query_params,
  get_list,
  handle_page_change,
  highlight_text
} = useCRUD({
  api_url: '/api/livestock/category/',
  refresh_signals: ['livestockcategory']
})

// 弹窗相关
const dialog_visible = ref(false)
const is_edit = ref(false)
const submit_loading = ref(false)
const upload_progress = ref(0)
const form_ref = ref()
const preview_url = ref('')
const selected_file = ref<File | null>(null)

const form = reactive({
  id: undefined,
  name: '',
  category_code: '',
  standard_cycle: 0,
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入大类名称', trigger: 'blur' }],
  category_code: [{ required: true, message: '请输入分类代码', trigger: 'blur' }]
}

// 处理图片选择
const handle_icon_change = (file: any) => {
  void (async () => {
    const raw_file = file?.raw as File | undefined
    if (!raw_file) return

    const result = await validate_image_file(raw_file)
    if (!result.ok) {
      ElMessage({ type: 'error', message: result.error_msg, customClass: 'error-message' })
      return
    }

    if (preview_url.value.startsWith('blob:')) {
      URL.revokeObjectURL(preview_url.value)
    }
    selected_file.value = raw_file
    preview_url.value = URL.createObjectURL(raw_file)
  })()
}

// 打开编辑弹窗
const handle_edit = (row: any) => {
  is_edit.value = true
  selected_file.value = null
  if (preview_url.value.startsWith('blob:')) {
    URL.revokeObjectURL(preview_url.value)
  }
  preview_url.value = row.icon || ''
  Object.assign(form, row)
  dialog_visible.value = true
}

// 提交表单
const handle_submit = async () => {
  if (!form_ref.value) return
  await form_ref.value.validate(async (valid: boolean) => {
    if (valid) {
      submit_loading.value = true
      upload_progress.value = 0
      try {
        const form_data = new FormData()
        form_data.append('name', form.name)
        form_data.append('category_code', form.category_code)
        form_data.append('standard_cycle', String(form.standard_cycle))
        form_data.append('description', form.description || '')
        
        if (selected_file.value) {
          form_data.append('icon', selected_file.value)
        }

        await request.put(`/api/livestock/category/${form.id}/`, form_data, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (evt: any) => {
            const total = evt?.total
            if (!total) return
            upload_progress.value = Math.min(99, Math.round((evt.loaded / total) * 100))
          }
        })
        ElMessage({ type: 'success', message: '修改成功', customClass: 'success-message' })
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

.category-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.card-image-wrapper {
  height: 140px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-icon-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: #909399;
}

.card-tag-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
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

.category-name {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.cycle-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
  background: #f0f9eb;
  padding: 6px 10px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.cycle-info .el-icon {
  color: #67c23a;
}

.cycle-info strong {
  color: #67c23a;
  font-size: 15px;
}

.category-icon-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 上传相关样式 */
.category-uploader {
  width: 120px;
  height: 120px;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.3s;
}

.category-uploader:hover {
  border-color: #409eff;
}

.uploader-icon {
  font-size: 28px;
  color: #8c939d;
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
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  gap: 8px;
}

.category-uploader:hover .upload-mask {
  opacity: 1;
}

.upload-mask .el-icon {
  font-size: 20px;
}

.upload-mask span {
    font-size: 12px;
  }

  .category-desc {
    font-size: 14px;
    color: #606266;
    line-height: 1.6;
    margin: 0 0 20px 0;
    display: -webkit-box;
    line-clamp: 2;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    flex: 1;
  }

  .card-footer {
    padding-top: 16px;
    border-top: 1px solid #f2f6fc;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .category-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #909399;
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

  .mr-1 {
    margin-right: 4px;
  }

  .form-tip {
    margin-top: 8px;
    font-size: 12px;
    color: #909399;
    line-height: 1.4;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }

  @media screen and (max-width: 768px) {
    .category-content {
      margin-top: 12px;
    }
  }
</style>
