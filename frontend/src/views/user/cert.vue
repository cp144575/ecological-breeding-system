<template>
  <PageContainer>
    <template #header_left>
      <h2>资质认证管理</h2>
    </template>
    <template #header_right>
      <el-input
        v-if="user_store.userInfo?.role === 'admin'"
        v-model="admin_search_input"
        placeholder="搜索养殖户姓名..."
        clearable
        class="search-input"
        :prefix-icon="Search"
        @clear="handle_admin_clear_search"
      />
    </template>

    <!-- 养殖户视角：显示自己的认证状态 -->
    <div v-if="user_store.userInfo?.role === 'farmer'" class="farmer-view" v-loading="loading_my_cert">
      <el-card v-if="my_cert && my_cert.id" class="standard-card status-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>我的认证详情</span>
            <el-tag :type="get_status_type(my_cert.status)" effect="dark">
              {{ get_status_label(my_cert.status) }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="windowWidth > 768 ? 2 : 1" border class="cert-descriptions">
          <el-descriptions-item label="提交时间">{{ format_date(my_cert.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="身份证号">
            <span>{{ maskIdCard(my_cert.id_card) }}</span>
            <p class="id-card-mask-tip">为保护隐私仅显示部分号码；重新提交时需完整填写 18 位身份证号</p>
          </el-descriptions-item>
          <el-descriptions-item label="审核备注" :span="2" v-if="my_cert.audit_remark">
            <span class="remark-text">{{ my_cert.audit_remark }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="资质文件" :span="2">
            <div class="cert-images-grid">
              <div class="cert-image-item">
                <div class="img-label">身份证正面</div>
                <el-image 
                  class="cert-img"
                  :src="my_cert.id_card_front" 
                  :preview-src-list="[my_cert.id_card_front]"
                  fit="cover"
                  preview-teleported
                />
              </div>
              <div class="cert-image-item">
                <div class="img-label">身份证反面</div>
                <el-image 
                  class="cert-img"
                  :src="my_cert.id_card_back" 
                  :preview-src-list="[my_cert.id_card_back]"
                  fit="cover"
                  preview-teleported
                />
              </div>
              <div class="cert-image-item">
                <div class="img-label">养殖许可证</div>
                <el-image 
                  class="cert-img"
                  :src="my_cert.breeding_license" 
                  :preview-src-list="[my_cert.breeding_license]"
                  fit="cover"
                  preview-teleported
                />
              </div>
            </div>
          </el-descriptions-item>
        </el-descriptions>
        <div v-if="my_cert.status === 2 || my_cert.status === 'rejected'" class="card-footer table-ops">
          <el-button class="btn-standard btn-add" @click="handle_upload">
            <el-icon><Refresh /></el-icon>重新提交认证
          </el-button>
        </div>
      </el-card>
      <el-empty v-else description="您尚未提交资质认证">
        <el-button class="btn-standard btn-add" @click="handle_upload">
          <el-icon><Plus /></el-icon>立即申请认证
        </el-button>
      </el-empty>
    </div>

    <!-- 管理员视角：待审核列表 -->
    <div v-else class="admin-view">
      <el-card class="standard-card">
        <el-tabs v-model="admin_active_tab" class="admin-tabs">
          <el-tab-pane label="待审核" name="0" />
          <el-tab-pane label="已通过" name="1" />
          <el-tab-pane label="已驳回" name="2" />
        </el-tabs>

        <transition name="tab-panel" mode="out-in">
          <div :key="admin_active_tab" v-loading="admin_tab_state.loading" class="cert-list-content">
            <el-row :gutter="20" v-if="admin_tab_state.list.length > 0">
              <el-col
                :xs="24"
                :sm="12"
                :md="8"
                :lg="6"
                v-for="item in admin_tab_state.list"
                :key="item.id"
                class="mb-4"
              >
                <el-card class="cert-card standard-card" shadow="hover">
                  <div class="card-header">
                    <span class="farmer-name" v-html="highlight_text(item.farmer_name, applied_admin_search_keyword)"></span>
                    <el-tag :type="get_status_type(item.status)" size="small" effect="plain">
                      {{ get_status_label(item.status) }}
                    </el-tag>
                  </div>
                  <div class="card-body">
                    <div class="info-item">
                      <span class="label">身份证号:</span>
                      <span class="value">{{ maskIdCard(item.id_card) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">提交时间:</span>
                      <span class="value">{{ format_date(item.created_at) }}</span>
                    </div>
                  </div>
                  <div class="card-footer table-ops">
                    <el-button class="btn-action-edit" link @click="handle_audit(item)">
                      <el-icon><View /></el-icon>{{ item.status === 0 || item.status === 'pending' ? '立即审核' : '查看详情' }}
                    </el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-empty v-else-if="!admin_tab_state.loading" description="暂无认证记录" />
          </div>
        </transition>

        <div class="pagination-container" v-if="user_store.userInfo?.role === 'admin'">
          <el-pagination
            :current-page="admin_tab_state.page"
            :page-size="cert_manage_store.page_size"
            layout="total, prev, pager, next"
            :total="admin_tab_state.total"
            @current-change="handle_admin_page_change"
            background
            size="small"
          />
        </div>
      </el-card>
    </div>

    <!-- 申请/重新提交弹窗 -->
    <el-dialog v-model="upload_visible" title="提交资质认证" width="600px">
      <el-form :model="upload_form" label-width="120px" ref="form_ref">
        <el-form-item label="身份证号" required>
          <el-input v-model="upload_form.id_card" placeholder="请输入18位身份证号" maxlength="18" />
        </el-form-item>
        
        <el-form-item label="身份证正面" required>
          <el-upload
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="(file: any) => handle_file_change(file, 'id_card_front')"
            accept="image/jpeg,image/png,image/gif"
            :multiple="true"
            :limit="10"
          >
            <el-button class="upload-button" type="primary">
              <el-icon><UploadFilled /></el-icon>
              上传图片
            </el-button>
          </el-upload>
          <el-image
            v-if="preview.id_card_front"
            :src="preview.id_card_front"
            :preview-src-list="[preview.id_card_front]"
            fit="cover"
            preview-teleported
            style="width: 200px; height: 120px; border-radius: 8px; margin-top: 12px;"
          />
        </el-form-item>

        <el-form-item label="身份证反面" required>
          <el-upload
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="(file: any) => handle_file_change(file, 'id_card_back')"
            accept="image/jpeg,image/png,image/gif"
            :multiple="true"
            :limit="10"
          >
            <el-button class="upload-button" type="primary">
              <el-icon><UploadFilled /></el-icon>
              上传图片
            </el-button>
          </el-upload>
          <el-image
            v-if="preview.id_card_back"
            :src="preview.id_card_back"
            :preview-src-list="[preview.id_card_back]"
            fit="cover"
            preview-teleported
            style="width: 200px; height: 120px; border-radius: 8px; margin-top: 12px;"
          />
        </el-form-item>

        <el-form-item label="养殖许可证" required>
          <el-upload
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="(file: any) => handle_file_change(file, 'breeding_license')"
            accept="image/jpeg,image/png,image/gif"
            :multiple="true"
            :limit="10"
          >
            <el-button class="upload-button" type="primary">
              <el-icon><UploadFilled /></el-icon>
              上传图片
            </el-button>
          </el-upload>
          <el-image
            v-if="preview.breeding_license"
            :src="preview.breeding_license"
            :preview-src-list="[preview.breeding_license]"
            fit="cover"
            preview-teleported
            style="width: 200px; height: 120px; border-radius: 8px; margin-top: 12px;"
          />
        </el-form-item>

        <el-form-item label="申请备注">
          <el-input v-model="upload_form.audit_remark" type="textarea" placeholder="可选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="upload_visible = false">取 消</el-button>
          <el-button class="btn-add" @click="submit_upload" :loading="submit_loading">提 交</el-button>
        </div>
        <el-progress v-if="submit_loading && upload_progress > 0" :percentage="upload_progress" :stroke-width="6" style="margin-top: 12px;" />
      </template>
    </el-dialog>

    <!-- 管理员审核/详情弹窗 -->
    <el-dialog v-model="audit_visible" title="认证详情" width="760px">
      <div v-loading="detail_loading">
        <el-descriptions v-if="current_cert" :column="windowWidth > 768 ? 2 : 1" border class="cert-descriptions">
          <el-descriptions-item label="养殖户">{{ current_cert.farmer_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ format_date(current_cert.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="身份证号" :span="2">
            <template v-if="user_store.userInfo?.role === 'admin' && current_cert.id_card_full">
              {{ current_cert.id_card_full }}
            </template>
            <template v-else>
              {{ maskIdCard(current_cert.id_card) || '-' }}
            </template>
          </el-descriptions-item>
          <el-descriptions-item label="审核状态">
            <el-tag :type="get_status_type(current_cert.status)" effect="dark">
              {{ get_status_label(current_cert.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="审核时间">{{ current_cert.audit_time ? format_date(current_cert.audit_time) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="审核备注" :span="2" v-if="current_cert.audit_remark">
            <span class="remark-text">{{ current_cert.audit_remark }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="认证图片" :span="2">
            <div class="cert-images-grid">
              <div class="cert-image-item">
                <div class="img-label">身份证正面</div>
                <el-image
                  v-if="current_cert.id_card_front"
                  class="cert-img"
                  :src="current_cert.id_card_front"
                  :preview-src-list="[current_cert.id_card_front]"
                  fit="cover"
                  preview-teleported
                />
                <div v-else class="img-label">未上传</div>
              </div>
              <div class="cert-image-item">
                <div class="img-label">身份证反面</div>
                <el-image
                  v-if="current_cert.id_card_back"
                  class="cert-img"
                  :src="current_cert.id_card_back"
                  :preview-src-list="[current_cert.id_card_back]"
                  fit="cover"
                  preview-teleported
                />
                <div v-else class="img-label">未上传</div>
              </div>
              <div class="cert-image-item">
                <div class="img-label">养殖许可证</div>
                <el-image
                  v-if="current_cert.breeding_license"
                  class="cert-img"
                  :src="current_cert.breeding_license"
                  :preview-src-list="[current_cert.breeding_license]"
                  fit="cover"
                  preview-teleported
                />
                <div v-else class="img-label">未上传</div>
              </div>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <el-form :model="audit_form" label-width="100px">
          <el-form-item label="审核结果" required>
            <el-radio-group v-model="audit_form.status">
              <el-radio :label="1">通过</el-radio>
              <el-radio :label="2">驳回</el-radio>
            </el-radio-group>
          </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="audit_form.audit_remark" type="textarea" placeholder="请输入审核意见" />
        </el-form-item>
      </el-form>
      </div>
      <template #footer>
        <el-button @click="audit_visible = false">取消</el-button>
        <el-button type="primary" @click="submit_audit" :loading="submit_loading">确定</el-button>
      </template>
    </el-dialog>
  </PageContainer>
</template>

<script setup lang="ts">
/**
 * 文件功能：用户资格认证管理页面
 */
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { debounce } from 'lodash-es'
import request from '@/utils/request'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { Plus, UploadFilled, Refresh, View, Search } from '@element-plus/icons-vue'
import PageContainer from '@/components/PageContainer.vue'
import { useCertManageStore } from '@/store/cert_manage'
import { format_date } from '@/utils/format'
import { validate_image_file } from '@/utils/image_upload'
import { maskIdCard } from '@/utils/mask_id_card'

const user_store = useUserStore()
const my_cert = ref<any>(null)

const cert_manage_store = useCertManageStore()

type admin_tab_key = '0' | '1' | '2'

const admin_active_tab = computed<admin_tab_key>({
  get: () => cert_manage_store.active_tab,
  set: (val: admin_tab_key) => {
    cert_manage_store.set_active_tab(val)
  }
})

const admin_tab_state = computed(() => cert_manage_store.tabs[admin_active_tab.value])

const applied_admin_search_keyword = computed(() => cert_manage_store.search_keyword)
const admin_search_input = ref('')

const sync_admin_search_input = () => {
  if (admin_search_input.value !== cert_manage_store.search_keyword) {
    admin_search_input.value = cert_manage_store.search_keyword
  }
}

sync_admin_search_input()

const reload_admin_by_search = debounce((keyword: string) => {
  void cert_manage_store.apply_search_and_reload(keyword)
}, 350)

watch(admin_search_input, (val) => {
  if (user_store.userInfo?.role !== 'admin') return
  reload_admin_by_search(val)
})

watch(admin_active_tab, () => {
  if (user_store.userInfo?.role !== 'admin') return
  void cert_manage_store.fetch_tab(admin_active_tab.value)
})

const handle_admin_clear_search = () => {
  reload_admin_by_search.cancel()
  admin_search_input.value = ''
  void cert_manage_store.apply_search_and_reload('')
}

const handle_admin_page_change = (page: number) => {
  if (user_store.userInfo?.role !== 'admin') return
  void cert_manage_store.fetch_tab(admin_active_tab.value, { force: true, page })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const escape_reg_exp = (text: string) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const highlight_text = (text: string, keyword: string) => {
  if (!text) return ''
  if (!keyword) return text
  const reg = new RegExp(`(${escape_reg_exp(keyword)})`, 'gi')
  return text.toString().replace(reg, `<mark class="highlight-keyword">$1</mark>`)
}

const get_my_cert = async () => {
  loading_my_cert.value = true
  try {
    const res: any = await request.get('/api/users/cert/my_cert/')
    my_cert.value = res
  } catch (error: any) {
    console.error('获取认证信息失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取认证信息失败')
  } finally {
    loading_my_cert.value = false
  }
}

const loading_my_cert = ref(false)

// 弹窗相关
const upload_visible = ref(false)
const audit_visible = ref(false)
const submit_loading = ref(false)
const upload_progress = ref(0)

const upload_form = reactive({
  id_card: '',
  id_card_front: null as any,
  id_card_back: null as any,
  breeding_license: null as any,
  audit_remark: ''
})

const preview = reactive({
  id_card_front: '',
  id_card_back: '',
  breeding_license: ''
})

const handle_file_change = (file: any, field: string) => {
  void (async () => {
    const raw_file = file?.raw as File | undefined
    if (!raw_file) return

    const result = await validate_image_file(raw_file)
    if (!result.ok) {
      ElMessage({ type: 'error', message: result.error_msg, customClass: 'error-message' })
      return
    }

    const previous_url = String((preview as any)[field] || '')
    if (previous_url.startsWith('blob:')) {
      URL.revokeObjectURL(previous_url)
    }

    ;(upload_form as any)[field] = raw_file
    ;(preview as any)[field] = URL.createObjectURL(raw_file)
  })()
}

const audit_form = reactive({
  id: undefined as number | undefined,
  status: 1 as number,
  audit_remark: ''
})

const current_cert = ref<any>(null)
const detail_loading = ref(false)

// 养殖户申请
const handle_upload = () => {
  const raw_id_card = my_cert.value?.id_card || ''
  upload_form.id_card = raw_id_card.includes('*') ? '' : raw_id_card
  upload_form.id_card_front = null
  upload_form.id_card_back = null
  upload_form.breeding_license = null
  upload_form.audit_remark = ''
  
  const urls = [preview.id_card_front, preview.id_card_back, preview.breeding_license]
  urls.forEach(url => {
    if (url && url.startsWith('blob:')) {
      URL.revokeObjectURL(url)
    }
  })

  preview.id_card_front = ''
  preview.id_card_back = ''
  preview.breeding_license = ''
  
  upload_visible.value = true
}

const submit_upload = async () => {
  if (!upload_form.id_card || upload_form.id_card.length !== 18 || upload_form.id_card.includes('*')) {
    ElMessage.warning('请输入正确的18位身份证号')
    return
  }
  if (!upload_form.id_card_front || !upload_form.id_card_back || !upload_form.breeding_license) {
    ElMessage.warning('请上传所有必要的资质照片')
    return
  }
  
  const formData = new FormData()
  formData.append('id_card', upload_form.id_card)
  formData.append('id_card_front', upload_form.id_card_front)
  formData.append('id_card_back', upload_form.id_card_back)
  formData.append('breeding_license', upload_form.breeding_license)
  formData.append('audit_remark', upload_form.audit_remark)

  submit_loading.value = true
  upload_progress.value = 0
  try {
    await request.post('/api/users/cert/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (evt: any) => {
        const total = evt?.total
        if (!total) return
        upload_progress.value = Math.min(99, Math.round((evt.loaded / total) * 100))
      }
    })
    ElMessage({ type: 'success', message: '申请提交成功，请等待管理员审核', customClass: 'success-message' })
    upload_visible.value = false
    void get_my_cert()
  } catch (error: any) {
    if (!error?.response) {
      ElMessage({ type: 'error', message: '上传失败，请重试', customClass: 'error-message' })
      return
    }
    ElMessage({
      type: 'error',
      message: error.response?.data?.detail || error.response?.data?.error || '提交失败',
      customClass: 'error-message'
    })
  } finally {
    upload_progress.value = 0
    submit_loading.value = false
  }
}

// 管理员审核
const handle_audit = (row: any) => {
  audit_form.id = row.id
  audit_form.status = row.status === 2 ? 2 : 1
  audit_form.audit_remark = ''
  detail_loading.value = true
  current_cert.value = null
  request
    .get(`/api/users/cert/${row.id}/`)
    .then((res: any) => {
      current_cert.value = res
      if (typeof res?.status === 'number' && [1, 2].includes(res.status)) {
        audit_form.status = res.status
      }
    })
    .catch(() => {
      ElMessage.error('获取认证详情失败')
    })
    .finally(() => {
      detail_loading.value = false
      audit_visible.value = true
    })
}

const submit_audit = async () => {
  submit_loading.value = true
  try {
    await request.post(`/api/users/cert/${audit_form.id}/audit/`, audit_form)
    ElMessage.success('审核操作成功')
    audit_visible.value = false
    void cert_manage_store.refresh_after_mutation()
  } catch (error) {
    console.error(error)
  } finally {
    submit_loading.value = false
  }
}

const get_status_label = (status: any) => {
  const map: any = {
    0: '待审核',
    1: '已通过',
    2: '已驳回',
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已驳回'
  }
  return map[status] || '未知'
}

const get_status_type = (status: any) => {
  const map: any = {
    0: 'info',
    1: 'success',
    2: 'danger',
    'pending': 'info',
    'approved': 'success',
    'rejected': 'danger'
  }
  return map[status] || 'info'
}

const windowWidth = ref(window.innerWidth)
const handleResize = () => {
  windowWidth.value = window.innerWidth
}

const init_page_data = async () => {
  if (!user_store.token) return

  if (!user_store.userInfo) {
    try {
      await user_store.getUserInfo()
    } catch {
      return
    }
  }

  if (user_store.userInfo?.role === 'admin') {
    sync_admin_search_input()
    void cert_manage_store.preload_all_tabs()
    return
  }

  void get_my_cert()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  void init_page_data()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  reload_admin_by_search.cancel()
  cert_manage_store.abort_all_requests()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.cert-descriptions {
  margin: 10px 0;
}

.remark-text {
  color: #f56c6c;
  font-weight: 500;
}

.cert-images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 10px 0;
}

.cert-image-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.img-label {
  font-size: 13px;
  color: #909399;
  text-align: center;
}

.cert-img {
  width: 100%;
  height: 140px;
  border-radius: 8px;
  cursor: zoom-in;
  transition: transform 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.cert-img:hover {
  transform: scale(1.02);
}

.card-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  justify-content: center;
}

.admin-tabs {
  margin-bottom: 20px;
}

.cert-list-content {
  margin-top: 8px;
  min-height: 240px;
}

.cert-card :deep(.el-card__body) {
  padding: 16px;
}

.farmer-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.card-body {
  padding: 12px 0;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item .label {
  color: #909399;
  width: 80px;
}

.info-item .value {
  color: #303133;
  flex: 1;
}

.mb-4 {
  margin-bottom: 16px;
}

/* 响应式适配 */
.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 200px;
  height: 120px;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: border-color 0.3s;
}
.avatar-uploader:hover {
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

:deep(.highlight-keyword) {
  background-color: #ffeb3b;
  color: #333;
  padding: 0 2px;
  border-radius: 2px;
}

.id-card-mask-tip {
  margin: 6px 0 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.tab-panel-enter-active,
.tab-panel-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tab-panel-enter-from,
.tab-panel-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .cert-images-grid {
    grid-template-columns: 1fr;
  }

  .cert-img {
    height: 180px;
  }

}
</style>
