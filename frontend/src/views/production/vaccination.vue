<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>疫苗接种管理</h2>
        <el-input
          v-model="query_params.search"
          placeholder="搜索批次号/疫苗名称"
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
      </div>
      <div class="header-right" v-if="user_store.userInfo?.role === 'farmer'">
        <el-button 
          class="btn-standard btn-add"
          :disabled="!user_store.userInfo?.profile?.is_verified"
          @click="handle_add"
        >
          <el-icon><Plus /></el-icon>新增登记
        </el-button>
      </div>
    </div>

    <el-card class="standard-card table-card" :body-style="{ padding: '0' }">
      <div class="mobile-list">
        <div v-for="item in vaccine_list" :key="item.id" class="mobile-card">
          <div class="mobile-card-header">
            <el-tag size="small" effect="plain">
              <span v-html="highlight_text(item.batch_code, query_params.search)"></span>
            </el-tag>
            <span class="date">{{ item.vaccination_date }}</span>
          </div>
          <div class="mobile-card-content">
            <div class="info-item" v-if="user_store.userInfo?.role === 'admin'">
              <span class="label">养殖户：</span>
              <span class="value">{{ item.farmer_name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">疫苗名称：</span>
              <span class="value" v-html="highlight_text(item.vaccine_name, query_params.search)"></span>
            </div>
            <div class="info-item" v-if="item.next_vaccination_date">
              <span class="label">下次接种：</span>
              <el-tag :type="is_expired(item.next_vaccination_date) ? 'danger' : 'warning'" size="small">
                {{ item.next_vaccination_date }}
              </el-tag>
            </div>
            <div class="info-item" v-if="item.remark">
              <span class="label">备注：</span>
              <span class="value">{{ item.remark }}</span>
            </div>
          </div>
          <div class="mobile-card-footer table-ops">
            <el-button class="btn-action-edit" link v-if="user_store.userInfo?.profile?.is_verified" @click="handle_edit(item)">编辑</el-button>
            <el-button class="btn-action-delete" link v-if="user_store.userInfo?.profile?.is_verified" @click="handle_delete(item.id, '确定要删除这条接种记录吗？')">删除</el-button>
          </div>
        </div>
        <el-empty v-if="!vaccine_list.length" description="暂无接种记录" />
      </div>

      <div class="pagination-container">
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
    </el-card>

    <!-- 接种登记弹窗 -->
    <el-dialog
      v-model="dialog_visible"
      :title="is_edit ? '修改接种记录' : '新增接种记录'"
      width="500px"
      class="standard-dialog"
    >
      <el-form :model="form" :rules="rules" ref="form_ref" label-width="100px" label-position="top">
        <el-form-item label="选择批次" prop="batch">
          <el-select v-model="form.batch" placeholder="请选择牲畜批次" style="width: 100%" filterable>
            <el-option
              v-for="item in batch_list"
              :key="item.id"
              :label="item.batch_code"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="疫苗名称" prop="vaccine_name">
          <el-input v-model="form.vaccine_name" placeholder="请输入疫苗名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="接种日期" prop="vaccination_date">
              <el-date-picker
                v-model="form.vaccination_date"
                type="date"
                placeholder="请选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="下次接种 (可选)" prop="next_vaccination_date">
              <el-date-picker
                v-model="form.next_vaccination_date"
                type="date"
                placeholder="请选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注说明" prop="remark">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注信息" resize="none" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog_visible = false">取 消</el-button>
          <el-button class="btn-add" @click="submit_form" :loading="submit_loading">确 定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：疫苗接种记录管理页面
 */
import { ref, onMounted, reactive } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useCRUD } from '@/hooks/useCRUD'
import { useUserStore } from '@/store/user'

const user_store = useUserStore()
const batch_list = ref<any[]>([])

// 使用通用 CRUD Hook
const {
  list: vaccine_list,
  total,
  query_params,
  get_list,
  handle_page_change,
  handle_delete,
  highlight_text,
  format_date: format_date_only
} = useCRUD({
  api_url: '/api/production/vaccination/',
  refresh_signals: ['vaccinationrecord']
})

const to_yyyy_mm_dd_or_empty = (value: any) => {
  if (!value) return ''
  if (value === '-') return ''
  const formatted = format_date_only(value)
  if (formatted === '-' || formatted === 'Invalid Date') return ''
  return formatted
}

// 弹窗相关
const dialog_visible = ref(false)
const is_edit = ref(false)
const submit_loading = ref(false)
const form_ref = ref()
const form = reactive({
  id: undefined,
  batch: undefined,
  vaccine_name: '',
  vaccination_date: format_date_only(new Date()),
  next_vaccination_date: null as string | null,
  remark: ''
})

const rules = {
  batch: [{ required: true, message: '请选择批次', trigger: 'change' }],
  vaccine_name: [{ required: true, message: '请输入疫苗名称', trigger: 'blur' }],
  vaccination_date: [{ required: true, message: '请选择接种日期', trigger: 'change' }]
}

// 获取批次列表
const get_batches = async () => {
  try {
    const res: any = await request.get('/api/livestock/batch/')
    batch_list.value = res.results || res
  } catch (error) {
    console.error(error)
  }
}

// 打开添加弹窗
const handle_add = () => {
  is_edit.value = false
  Object.assign(form, {
    id: undefined,
    batch: undefined,
    vaccine_name: '',
    vaccination_date: format_date_only(new Date()),
    next_vaccination_date: null,
    remark: ''
  })
  dialog_visible.value = true
}

// 打开编辑弹窗
const handle_edit = (row: any) => {
  is_edit.value = true
  Object.assign(form, {
    ...row,
    vaccination_date: to_yyyy_mm_dd_or_empty(row?.vaccination_date),
    next_vaccination_date: to_yyyy_mm_dd_or_empty(row?.next_vaccination_date) || null
  })
  dialog_visible.value = true
}

// 提交表单
const submit_form = async () => {
  if (!form_ref.value) return
  await form_ref.value.validate(async (valid: boolean) => {
    if (valid) {
      submit_loading.value = true
      try {
        const payload = {
          batch: form.batch,
          vaccine_name: form.vaccine_name,
          vaccination_date: to_yyyy_mm_dd_or_empty(form.vaccination_date),
          next_vaccination_date: to_yyyy_mm_dd_or_empty(form.next_vaccination_date) || null,
          remark: form.remark
        }

        if (!payload.vaccination_date) {
          ElMessage.warning('请选择接种日期')
          return
        }

        if (is_edit.value) {
          await request.put(`/api/production/vaccination/${form.id}/`, payload)
          ElMessage.success('修改成功')
        } else {
          await request.post('/api/production/vaccination/', payload)
          ElMessage.success('登记成功')
        }
        dialog_visible.value = false
        get_list()
      } catch (error) {
        console.error(error)
      } finally {
        submit_loading.value = false
      }
    }
  })
}

const is_expired = (date: string) => {
  if (!date) return false
  const today = format_date_only(new Date())
  return date < today
}

onMounted(() => {
  get_batches()
})
</script>

<style scoped>
.page-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.header-section {
  margin-bottom: 24px;
}

.header-title h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
  font-weight: 600;
}

.header-subtitle {
  color: #909399;
  font-size: 14px;
  margin-top: 4px;
  display: block;
}

.search-input {
  width: 280px;
}

.table-card {
  border-radius: 8px;
  overflow: hidden;
}

.vaccine-info, .date-info {
  display: flex;
  align-items: center;
  justify-content: center;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  background: #fff;
}

/* 移动端卡片样式 */
.mobile-list {
  padding: 12px;
  background: #f5f7fa;
}

.mobile-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

.mobile-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f2f6fc;
}

.mobile-card-content .info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.mobile-card-content .label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.mobile-card-content .value {
  color: #303133;
}

.text-danger {
  color: #f56c6c;
  font-weight: 600;
}

.mr-1 { margin-right: 0.25rem; }

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
  
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .search-input {
    width: 100% !important;
    margin-right: 0 !important;
    margin-bottom: 12px;
  }
}
</style>
