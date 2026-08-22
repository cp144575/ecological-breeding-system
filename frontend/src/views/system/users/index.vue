<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>用户账户管理</h2>
        <el-input 
          v-model="query_params.search" 
          placeholder="搜索用户名/手机号..." 
          clearable 
          :prefix-icon="Search"
          class="search-input"
        />
      </div>
      <div class="header-right">
      </div>
    </div>

    <div v-loading="loading" class="user-content">
      <el-row :gutter="20" v-if="list_data.length > 0">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in list_data" :key="item.id" class="mb-4">
          <el-card class="user-card standard-card" shadow="hover">
            <div class="title-row">
              <span class="username" v-html="highlight_keyword(item.username, query_params.search)"></span>
              <el-tag :type="item.is_active ? 'success' : 'info'" size="small" effect="plain">
                {{ item.is_active ? '启用' : '禁用' }}
              </el-tag>
            </div>
            <div class="card-body">
              <div class="info-item">
                <span class="label">手机号:</span>
                <span class="value" v-html="highlight_keyword(item.phone, query_params.search)"></span>
              </div>
              <div class="info-item">
                <span class="label">角色:</span>
                <el-tag :type="item.role === 'admin' ? 'danger' : (item.role === 'vet' ? 'warning' : 'success')" size="small" effect="plain">
                  {{ item.role === 'admin' ? '管理员' : (item.role === 'vet' ? '兽医' : '养殖户') }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="label">注册时间:</span>
                <span class="value">{{ format_date(item.date_joined) }}</span>
              </div>
            </div>
            <div class="card-footer table-ops">
              <el-button link class="btn-action-edit" @click="handle_edit(item)">
                编辑
              </el-button>
              <el-button 
                link 
                class="btn-action-edit"
                @click="handle_toggle_active(item)"
                :disabled="item.id === user_store.userInfo?.id"
              >
                <el-icon><SwitchButton /></el-icon>
                {{ item.is_active ? '禁用账户' : '启用账户' }}
              </el-button>
              <el-button
                link
                class="btn-action-delete"
                @click="handle_delete_user(item)"
                :disabled="item.id === user_store.userInfo?.id"
              >
                删除
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-else-if="!loading" description="暂无用户数据" />

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

    <el-dialog v-model="edit_visible" title="编辑用户" width="520px" destroy-on-close>
      <el-form :model="edit_form" label-width="90px" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="edit_form.username" disabled />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="edit_form.phone" placeholder="可为空" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="edit_form.email" placeholder="可为空" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="edit_form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="edit_visible = false">取消</el-button>
        <el-button type="primary" :loading="edit_saving" @click="submit_edit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：账户管理页面 (仅限管理员)
 */
import { ref, reactive } from 'vue'
import { useUserStore } from '@/store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { SwitchButton, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useCRUD } from '@/hooks/useCRUD'

const user_store = useUserStore()

// 使用通用 CRUD hook
const {
  loading,
  list: list_data,
  total,
  query_params,
  get_list,
  handle_page_change,
  highlight_text: highlight_keyword,
  format_date_time: format_date
} = useCRUD({ 
  api_url: '/api/users/profile/',
  refresh_signals: ['user']
})

const handle_toggle_active = (row: any) => {
  const action = row.is_active ? '禁用' : '启用'
  ElMessageBox.confirm(`确定要${action}用户 "${row.username}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.post(`/api/users/profile/${row.id}/toggle_active/`)
      ElMessage.success(`用户已${action}`)
      get_list()
    } catch (error) {
      console.error(error)
    }
  }).catch(() => {})
}

const edit_visible = ref(false)
const edit_saving = ref(false)
const edit_form = reactive({
  id: 0,
  username: '',
  phone: '',
  email: '',
  is_active: true
})

const handle_edit = (row: any) => {
  edit_form.id = row.id
  edit_form.username = row.username
  edit_form.phone = row.phone || ''
  edit_form.email = row.email || ''
  edit_form.is_active = Boolean(row.is_active)
  edit_visible.value = true
}

const submit_edit = async () => {
  edit_saving.value = true
  try {
    await request.patch(`/api/users/profile/${edit_form.id}/`, {
      phone: edit_form.phone || null,
      email: edit_form.email || '',
      is_active: edit_form.is_active
    })
    ElMessage.success('保存成功')
    edit_visible.value = false
    get_list()
  } catch (_error) {
    ElMessage.error('保存失败')
  } finally {
    edit_saving.value = false
  }
}

const handle_delete_user = (row: any) => {
  ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？此操作不可恢复。`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await request.delete(`/api/users/profile/${row.id}/`)
      ElMessage.success('删除成功')
      get_list()
    } catch (_error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
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
  margin: 0;
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

.standard-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.table-card {
  margin-top: 20px;
}

.user-content {
  margin-top: 20px;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  background: #fff;
}

/* 移动端卡片样式 */
.user-card :deep(.el-card__body) {
  padding: 16px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.title-row .username {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
  align-items: center;
}

.info-item .label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.info-item .value {
  color: #303133;
}

.card-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f2f6fc;
  display: flex;
  justify-content: flex-end;
}


.mr-1 {
  margin-right: 4px;
}

.mb-4 {
  margin-bottom: 16px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .header-section {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
  }

  .search-input {
    width: 100% !important;
  }

}
</style>
