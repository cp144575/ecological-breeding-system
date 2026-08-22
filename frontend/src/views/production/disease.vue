<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>疾病上报与处理</h2>
        <el-input
          v-model="query_params.search"
          placeholder="搜索疾病名称/症状/批次号"
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
      </div>
      <div class="header-right">
        <el-button 
          v-if="user_store.userInfo?.role === 'farmer'"
          class="btn-standard btn-add"
          style="background-color: var(--danger-color) !important; border-color: var(--danger-color) !important;"
          :disabled="!user_store.userInfo?.profile?.is_verified"
          @click="handle_add"
        >
          <el-icon><Warning /></el-icon>疾病上报
        </el-button>
      </div>
    </div>

    <el-card class="standard-card table-card" :body-style="{ padding: '0' }">
      <div class="mobile-list">
        <div v-for="item in disease_list" :key="item.id" class="mobile-card">
          <div class="mobile-card-header">
            <el-tag size="small" effect="plain">
              <span v-html="highlight_text(item.batch_code, query_params.search)"></span>
            </el-tag>
            <el-tag :type="get_status_type(item.status)" effect="dark" size="small">
              {{ get_status_label(item.status) }}
            </el-tag>
          </div>
          <div class="mobile-card-content">
            <div class="info-item" v-if="user_store.userInfo?.role === 'admin' || user_store.userInfo?.role === 'vet'">
              <span class="label">养殖户：</span>
              <span class="value">{{ item.farmer_name || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">疾病名称：</span>
              <span class="value" v-html="highlight_text(item.disease_name, query_params.search)"></span>
            </div>
            <div class="info-item" v-if="item.symptoms">
              <span class="label">症状：</span>
              <span class="value" v-html="highlight_text(item.symptoms, query_params.search)"></span>
            </div>
            <div class="info-item">
              <span class="label">影响数量：</span>
              <span class="value highlight">{{ item.affected_count }}</span>
            </div>
            <div class="info-item">
              <span class="label">上报日期：</span>
              <span class="value">{{ item.report_date }}</span>
            </div>
          </div>
          <div class="mobile-card-footer table-ops">
            <el-button class="btn-action-edit" link v-if="user_store.userInfo?.role === 'admin' && item.status !== 'recovered' && item.status !== 'died'" @click="handle_assign(item)">分配</el-button>
            <el-button class="btn-action-edit" link v-if="user_store.userInfo?.role === 'vet' && item.status !== 'recovered' && item.status !== 'died'" @click="handle_audit(item)">处理</el-button>
            <el-button class="btn-action-view" link @click="handle_edit(item)">查看</el-button>
            <el-button class="btn-action-delete" link v-if="user_store.userInfo?.role === 'admin' || user_store.userInfo?.profile?.is_verified" @click="handle_delete(item.id, '确定要删除这条疾病上报记录吗？')">删除</el-button>
          </div>
        </div>
        <el-empty v-if="!disease_list.length" description="暂无记录" />
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

    <!-- 上报/编辑弹窗 -->
    <el-dialog
      v-model="dialog_visible"
      :title="is_edit ? '疾病详情' : '疾病上报'"
      width="600px"
      class="standard-dialog"
    >
      <el-form :model="form" :rules="rules" ref="form_ref" label-width="100px" label-position="top">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="选择批次" prop="batch">
              <el-select v-model="form.batch" placeholder="请选择批次" style="width: 100%" :disabled="is_edit" filterable>
                <el-option
                  v-for="item in batch_list"
                  :key="item.id"
                  :label="item.batch_code"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="疾病名称" prop="disease_name">
              <el-input v-model="form.disease_name" placeholder="请输入疾病名称" :disabled="is_edit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="影响数量" prop="affected_count">
              <el-input-number v-model="form.affected_count" :min="1" style="width: 100%" :disabled="is_edit" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="is_edit">
            <el-form-item label="上报日期" prop="report_date">
              <el-input v-model="form.report_date" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="详细症状" prop="symptoms">
              <el-input v-model="form.symptoms" type="textarea" :rows="4" placeholder="请详细描述症状" :disabled="is_edit" resize="none" />
            </el-form-item>
          </el-col>

          <el-col :span="24" v-if="is_edit">
            <el-form-item label="处理状态" prop="status">
              <el-tag :type="get_status_type(form.status)" effect="dark">{{ get_status_label(form.status) }}</el-tag>
            </el-form-item>
          </el-col>

          <el-col :span="24" v-if="is_edit && (form.treatment_plan || form.handled_at || form.handled_by_name)">
          <el-form-item label="处理意见">
              <el-input v-model="form.treatment_plan" type="textarea" :rows="4" disabled resize="none" placeholder="暂无" />
          </el-form-item>
          </el-col>

          <el-col :span="12" v-if="is_edit && (form.handled_by_name || form.handled_at)">
            <el-form-item label="处理人">
              <el-input v-model="form.handled_by_name" disabled placeholder="-" />
            </el-form-item>
          </el-col>

          <el-col :span="12" v-if="is_edit && (form.handled_by_name || form.handled_at)">
            <el-form-item label="处理时间">
              <el-input :model-value="format_date_time(form.handled_at, 'YYYY-MM-DD')" disabled placeholder="-" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog_visible = false">{{ is_edit ? '关闭' : '取消' }}</el-button>
          <el-button v-if="!is_edit" class="btn-add" @click="submit_form" :loading="submit_loading">提交上报</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 管理员分配弹窗 -->
    <el-dialog
      v-model="assign_visible"
      title="分配给兽医"
      width="500px"
      class="standard-dialog"
    >
      <el-form :model="assign_form" label-width="100px" label-position="top">
        <el-form-item label="选择兽医">
          <el-select v-model="assign_form.vet_user_id" placeholder="请选择兽医" style="width: 100%" filterable>
            <el-option
              v-for="item in vet_user_list"
              :key="item.id"
              :label="item.username"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="assign_visible = false">取消</el-button>
          <el-button type="primary" @click="submit_assign" :loading="submit_loading">确认分配</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 管理员处理弹窗 -->
    <el-dialog
      v-model="audit_visible"
      title="处理疾病报告"
      width="500px"
      class="standard-dialog"
    >
      <el-form :model="audit_form" label-width="100px" label-position="top">
        <el-form-item label="处理状态更新">
          <el-radio-group v-model="audit_form.status">
            <el-radio-button label="treating">处理中</el-radio-button>
            <el-radio-button label="recovered">已康复</el-radio-button>
            <el-radio-button label="died">死亡</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="治疗方案与建议">
          <el-input v-model="audit_form.treatment_plan" type="textarea" :rows="4" placeholder="请输入具体的治疗方案或改进建议" resize="none" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="audit_visible = false">取消</el-button>
          <el-button type="primary" @click="submit_audit" :loading="submit_loading">确认处理</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：疾病上报与处理管理页面
 */
import { ref, onMounted, reactive } from 'vue'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { useCRUD } from '@/hooks/useCRUD'
import { format_date_time } from '@/utils/format'
import { Warning, Search } from '@element-plus/icons-vue'

const user_store = useUserStore()
const batch_list = ref<any[]>([])

// 使用通用 CRUD Hook
const {
  list: disease_list,
  total,
  query_params,
  get_list,
  handle_page_change,
  handle_delete,
  highlight_text,
} = useCRUD({
  api_url: '/api/production/disease/',
  refresh_signals: ['diseasereport']
})

// 弹窗相关
const dialog_visible = ref(false)
const is_edit = ref(false)
const audit_visible = ref(false)
const assign_visible = ref(false)
const submit_loading = ref(false)
const form_ref = ref()
const form = reactive({
  id: undefined,
  batch: undefined,
  disease_name: '',
  affected_count: 1,
  symptoms: '',
  report_date: '',
  status: 'pending',
  treatment_plan: '',
  handled_by_name: '',
  handled_at: ''
})

const audit_form = reactive({
  id: undefined,
  status: 'treating',
  treatment_plan: ''
})

const assign_form = reactive({
  id: undefined,
  vet_user_id: undefined,
})

const vet_user_list = ref<any[]>([])

const rules = {
  batch: [{ required: true, message: '请选择批次', trigger: 'change' }],
  disease_name: [{ required: true, message: '请输入疾病名称', trigger: 'blur' }],
  symptoms: [{ required: true, message: '请描述症状', trigger: 'blur' }]
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

// 打开上报弹窗
const handle_add = () => {
  is_edit.value = false
  Object.assign(form, {
    id: undefined,
    batch: undefined,
    disease_name: '',
    affected_count: 1,
    symptoms: '',
    report_date: new Date().toISOString().split('T')[0],
    status: 'pending',
    treatment_plan: '',
    handled_by_name: '',
    handled_at: ''
  })
  dialog_visible.value = true
}

// 查看详情
const handle_edit = (row: any) => {
  is_edit.value = true
  Object.assign(form, row)
  dialog_visible.value = true
}

// 提交上报
const submit_form = async () => {
  if (!form_ref.value) return
  await form_ref.value.validate(async (valid: boolean) => {
    if (valid) {
      submit_loading.value = true
      try {
        const payload = {
          batch: form.batch,
          disease_name: form.disease_name,
          affected_count: form.affected_count,
          symptoms: form.symptoms,
          report_date: form.report_date || new Date().toISOString().split('T')[0],
        }
        await request.post('/api/production/disease/', payload)
        ElMessage.success('上报成功，请等待兽医处理')
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

const get_vet_users = async () => {
  try {
    const res: any = await request.get('/api/users/profile/', { params: { page_size: 200 } })
    const raw_list = res?.results || res || []
    vet_user_list.value = (Array.isArray(raw_list) ? raw_list : []).filter((item: any) => item?.role === 'vet' && item?.is_active)
  } catch (error) {
    console.error(error)
  }
}

const handle_assign = (row: any) => {
  assign_form.id = row.id
  assign_form.vet_user_id = row.handled_by || undefined
  assign_visible.value = true
  if (!vet_user_list.value.length) {
    get_vet_users()
  }
}

const submit_assign = async () => {
  if (!assign_form.vet_user_id) {
    ElMessage.warning('请选择兽医')
    return
  }
  submit_loading.value = true
  try {
    await request.post(`/api/production/disease/${assign_form.id}/assign/`, { vet_user_id: assign_form.vet_user_id })
    ElMessage.success('分配成功')
    assign_visible.value = false
    get_list()
  } catch (error) {
    console.error(error)
  } finally {
    submit_loading.value = false
  }
}

// 打开审核弹窗
const handle_audit = (row: any) => {
  audit_form.id = row.id
  audit_form.status = row.status === 'pending' ? 'treating' : (row.status || 'treating')
  audit_form.treatment_plan = row.treatment_plan || ''
  audit_visible.value = true
}

// 提交审核
const submit_audit = async () => {
  submit_loading.value = true
  try {
    await request.post(`/api/production/disease/${audit_form.id}/audit/`, audit_form)
    ElMessage.success('处理成功')
    audit_visible.value = false
    get_list()
  } catch (error) {
    console.error(error)
  } finally {
    submit_loading.value = false
  }
}

const get_status_type = (status: string) => {
  const map: any = {
    pending: 'danger',
    treating: 'warning',
    recovered: 'success',
    died: 'danger'
  }
  return map[status] || 'info'
}

const get_status_label = (status: string) => {
  const map: any = {
    pending: '待处理',
    treating: '处理中',
    recovered: '已康复',
    died: '死亡'
  }
  return map[status] || status
}

onMounted(() => {
  if (user_store.userInfo?.role === 'farmer') {
    get_batches()
  }

  if (user_store.userInfo?.role === 'admin') {
    get_vet_users()
  }
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

.disease-name {
  font-weight: 500;
  color: #2c3e50;
}

.count-text {
  font-weight: 600;
  color: #f56c6c;
}

.symptoms-text {
  color: #606266;
  line-height: 1.6;
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
}

.mobile-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
  border: 1px solid #ebeef5;
}

.mobile-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f2f5;
}

.mobile-card-content {
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.4;
}

.info-item .label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.info-item .value {
  color: #303133;
}

.info-item .value.highlight {
  color: #f56c6c;
  font-weight: 600;
}

.symptoms-summary {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: #606266 !important;
}

.mobile-card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f2f5;
}

.standard-dialog :deep(.el-form-item__label) {
  font-weight: 600;
}

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
  }
}
</style>
