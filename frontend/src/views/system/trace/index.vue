<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>溯源管理</h2>
        <el-input
          v-model="query_params.search"
          placeholder="搜索溯源码、批次号..."
          clearable
          class="search-input"
          :prefix-icon="Search"
        />
      </div>
    </div>

    <div v-loading="loading" class="trace-content">
      <el-row :gutter="20" v-if="trace_list.length > 0">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in trace_list" :key="item.id" class="mb-4">
          <el-card class="trace-card standard-card" shadow="hover">
            <div class="card-header">
              <div class="card-title" v-html="highlight_text(item.trace_code, query_params.search)"></div>
              <el-tag :type="item.is_active ? 'success' : 'info'" size="small" effect="plain">
                {{ item.is_active ? '启用' : '禁用' }}
              </el-tag>
            </div>
            <div class="card-body">
              <div class="info-item">
                <span class="label">批次号:</span>
                <span class="value" v-html="highlight_text(item.batch_code, query_params.search)"></span>
              </div>
              <div class="info-item">
                <span class="label">养殖户:</span>
                <span class="value">{{ item.farmer_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">生成时间:</span>
                <span class="value">{{ format_date_time(item.created_at) }}</span>
              </div>
            </div>
            <div class="card-footer table-ops">
              <el-button link class="btn-action-view" @click="copy_trace_link(item.trace_code)">复制链接</el-button>
              <el-button link class="btn-action-view" @click="show_certificate(item)">合格证</el-button>
              <el-button link class="btn-action-delete" @click="handle_delete(item.id)">删除</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-else-if="!loading" description="暂无溯源数据" />

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
      v-model="cert_visible"
      title="生态养殖溯源合格证"
      width="500px"
      class="cert-dialog"
      destroy-on-close
    >
      <div v-loading="cert_loading" class="cert-wrapper">
        <div v-if="current_batch" class="cert-container" id="cert-content">
          <div class="cert-header">
            <div class="cert-logo">
              <el-icon size="40" color="#67C23A"><Opportunity /></el-icon>
              <h3>生态养殖管理系统</h3>
            </div>
            <div class="cert-title">产地直供 · 质量溯源</div>
          </div>

          <div class="cert-body">
            <div class="cert-row">
              <span class="cert-label">产品名称:</span>
              <span class="cert-value">{{ (current_batch.category_name || current_batch.livestock_type || '生态养殖批次') }} ({{ current_batch.breed || '-' }})</span>
            </div>
            <div class="cert-row">
              <span class="cert-label">批次编号:</span>
              <span class="cert-value">{{ current_batch.batch_code }}</span>
            </div>
            <div class="cert-row">
              <span class="cert-label">溯源编码:</span>
              <span class="cert-value code">{{ current_batch.trace_code || '待生成' }}</span>
            </div>
            <div class="cert-row">
              <span class="cert-label">生态等级:</span>
              <span class="cert-value">
                <el-rate :model-value="format_eco_score(current_batch.eco_score)" disabled allow-half />
                <span style="margin-left: 8px">{{ format_eco_score(current_batch.eco_score) }} / 5</span>
              </span>
            </div>
            <div class="cert-row">
              <span class="cert-label">养殖区域:</span>
              <span class="cert-value">{{ current_batch.area_name }}</span>
            </div>
            <div class="cert-row">
              <span class="cert-label">入栏日期:</span>
              <span class="cert-value">{{ current_batch.entry_date }}</span>
            </div>
            <div v-if="current_batch.status === 'finished'" class="cert-row">
              <span class="cert-label">出栏日期:</span>
              <span class="cert-value">{{ current_batch.finish_date }}</span>
            </div>

            <div class="cert-footer">
              <div class="cert-qrcode">
                <template v-if="get_batch_trace_url(current_batch)">
                  <QrcodeVue :value="get_batch_trace_url(current_batch)" :size="80" level="H" render-as="canvas" />
                  <span>扫码核验</span>
                </template>
                <template v-else>
                  <el-tag type="warning" effect="plain" size="small">溯源码生成中</el-tag>
                  <span>请稍后刷新溯源列表</span>
                </template>
              </div>
              <div class="cert-stamp">
                <div class="stamp-inner">
                  <p>{{ current_batch.farmer_name || '-' }}</p>
                  <p>质量合格章</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <el-empty v-else description="暂无合格证数据" />
      </div>

      <template #footer>
        <el-button @click="cert_visible = false">关闭</el-button>
        <el-button v-if="current_batch?.trace_code" @click="copy_trace_link(String(current_batch.trace_code))">复制溯源链接</el-button>
        <el-button v-if="current_batch?.trace_code" @click="download_cert">下载证书</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Opportunity, Search } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useCRUD } from '@/hooks/useCRUD'
import QrcodeVue from 'qrcode.vue'

const {
  loading,
  list: trace_list,
  total,
  query_params,
  handle_page_change,
  handle_delete,
  highlight_text,
  format_date_time
} = useCRUD({
  api_url: '/api/traceability/admin/',
  refresh_signals: ['trace']
})

const copy_to_clipboard = async (text: string) => {
  if (!text) return false

  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      return true
    }
  } catch (_error) {
  }

  try {
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.setAttribute('readonly', '')
    textarea.style.position = 'fixed'
    textarea.style.left = '-1000px'
    textarea.style.top = '-1000px'
    document.body.appendChild(textarea)
    textarea.focus()
    textarea.select()
    textarea.setSelectionRange(0, text.length)
    const ok = document.execCommand('copy')
    document.body.removeChild(textarea)
    return ok
  } catch (_error) {
    return false
  }
}

const get_trace_url = (code: string | undefined | null) => {
  if (!code) return ''
  return `${window.location.origin}/public/trace/${code}`
}

const get_batch_trace_url = (batch_data: any) => {
  const trace_url = String(batch_data?.trace_url || '').trim()
  if (trace_url) {
    return trace_url
  }
  return get_trace_url(batch_data?.trace_code)
}

const copy_trace_link = (code: string | undefined | null) => {
  const url = get_trace_url(code)
  if (!url) {
    ElMessage.warning('溯源码无效，无法复制')
    return
  }

  void (async () => {
    const ok = await copy_to_clipboard(url)
    if (ok) {
      ElMessage.success('溯源链接已复制到剪贴板')
      return
    }
    ElMessage.error('复制失败，请长按/手动复制链接')
  })()
}

const cert_visible = ref(false)
const cert_loading = ref(false)
const current_batch = ref<any>(null)

const format_eco_score = (value: any) => {
  const numeric_value = Number(value)
  if (Number.isNaN(numeric_value)) return 0
  const clamped = Math.min(5, Math.max(0, numeric_value))
  return Math.round(clamped * 2) / 2
}

const show_certificate = async (row: any) => {
  const batch_id = row?.batch
  if (!batch_id) {
    ElMessage.warning('缺少批次信息，无法查看合格证')
    return
  }

  cert_visible.value = true
  cert_loading.value = true
  current_batch.value = null
  try {
    const res: any = await request.get(`/api/livestock/batch/${batch_id}/`)
    current_batch.value = res
  } catch (_error) {
    ElMessage.error('获取合格证数据失败')
  } finally {
    cert_loading.value = false
  }
}

const download_cert = async () => {
  if (!current_batch.value?.trace_code) {
    ElMessage.warning('溯源码尚未生成，无法下载证书')
    return
  }

  const cert_container = document.getElementById('cert-content')
  if (!cert_container) {
    ElMessage.error('未找到证书内容')
    return
  }

  const export_date = new Date().toISOString().slice(0, 10)
  const batch_code = String(current_batch.value?.batch_code || '')
  const trace_code = String(current_batch.value?.trace_code || '')
  const trace_url = get_batch_trace_url(current_batch.value)

  let qr_data_url = ''
  const original_canvas = cert_container.querySelector('canvas') as HTMLCanvasElement | null
  qr_data_url = original_canvas ? original_canvas.toDataURL('image/png') : ''

  const eco_score = format_eco_score(current_batch.value?.eco_score)
  const batch_name = String(current_batch.value?.category_name || current_batch.value?.livestock_type || '生态养殖批次')
  const batch_breed = String(current_batch.value?.breed || '')
  const area_name = String(current_batch.value?.area_name || '')
  const entry_date = String(current_batch.value?.entry_date || '')
  const finish_date = String(current_batch.value?.finish_date || '')
  const farmer_name = String(current_batch.value?.farmer_name || '')
  const batch_image = String(current_batch.value?.image || '')

  const certificate_css = `
    body { margin: 0; padding: 24px; background: #f6f8fa; color: #303133; font-family: "Microsoft YaHei", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
    .page { max-width: 720px; margin: 0 auto; }
    .cert-container { padding: 30px; background: #fff; border: 4px double #67C23A; border-radius: 4px; position: relative; }
    .cert-header { text-align: center; border-bottom: 2px solid #67C23A; padding-bottom: 20px; margin-bottom: 25px; }
    .cert-logo { display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 8px; }
    .cert-logo .logo-mark { width: 36px; height: 36px; border-radius: 10px; background: #67C23A; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; }
    .cert-logo h3 { margin: 0; color: #67C23A; font-size: 22px; letter-spacing: 2px; }
    .cert-title { font-size: 14px; color: #909399; letter-spacing: 4px; }
    .cert-body { display: flex; flex-direction: column; gap: 18px; }
    .cert-row { display: flex; align-items: center; font-size: 15px; }
    .cert-label { color: #606266; width: 92px; font-weight: bold; }
    .cert-value { color: #303133; flex: 1; }
    .cert-value.code { font-family: monospace; background: #f4f4f5; padding: 2px 8px; border-radius: 4px; color: #e6a23c; }
    .cert-value .stars { color: #f7ba2a; letter-spacing: 2px; font-size: 16px; }
    .cert-image { margin-top: 4px; width: 100%; max-height: 240px; border-radius: 10px; object-fit: cover; border: 1px solid #f0f2f5; }
    .cert-footer { margin-top: 30px; display: flex; justify-content: space-between; align-items: flex-end; padding-top: 20px; border-top: 1px dashed #dcdfe6; }
    .cert-qrcode { display: flex; flex-direction: column; align-items: center; gap: 8px; }
    .cert-qrcode img { width: 80px; height: 80px; border: 1px solid #f0f2f5; border-radius: 6px; }
    .cert-qrcode span { font-size: 12px; color: #909399; }
    .cert-stamp { width: 120px; height: 120px; border: 3px solid rgba(245, 108, 108, 0.6); border-radius: 50%; display: flex; align-items: center; justify-content: center; transform: rotate(-15deg); }
    .cert-stamp .stamp-inner { text-align: center; color: rgba(245, 108, 108, 0.8); font-weight: bold; }
    .cert-stamp .stamp-inner p { margin: 0; font-size: 13px; }
    .trace-url { margin-top: 12px; color: #909399; font-size: 12px; text-align: center; word-break: break-all; }
    @media print { body { background: #fff; padding: 0; } }
  `

  const full_star_count = Math.floor(eco_score)
  const half_star = eco_score - full_star_count >= 0.5
  const star_text = `${'★'.repeat(full_star_count)}${half_star ? '☆' : ''}`

  const html = `<!doctype html>
  <html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>生态养殖溯源合格证_${batch_code}_${export_date}</title>
    <style>
      ${certificate_css}
    </style>
  </head>
  <body>
    <div class="page">
      <div class="cert-container">
        <div class="cert-header">
          <div class="cert-logo">
            <div class="logo-mark">ECO</div>
            <h3>生态养殖管理系统</h3>
          </div>
          <div class="cert-title">产地直供 · 质量溯源</div>
        </div>

        <div class="cert-body">
          <div class="cert-row">
            <span class="cert-label">产品名称:</span>
            <span class="cert-value">${batch_name} (${batch_breed})</span>
          </div>
          <div class="cert-row">
            <span class="cert-label">批次编号:</span>
            <span class="cert-value">${batch_code}</span>
          </div>
          <div class="cert-row">
            <span class="cert-label">溯源编码:</span>
            <span class="cert-value code">${trace_code}</span>
          </div>
          <div class="cert-row">
            <span class="cert-label">生态等级:</span>
            <span class="cert-value"><span class="stars">${star_text}</span> <span style="margin-left: 8px; color: #606266;">${eco_score} / 5</span></span>
          </div>
          <div class="cert-row">
            <span class="cert-label">养殖区域:</span>
            <span class="cert-value">${area_name}</span>
          </div>
          <div class="cert-row">
            <span class="cert-label">入栏日期:</span>
            <span class="cert-value">${entry_date}</span>
          </div>
          ${finish_date ? `
          <div class="cert-row">
            <span class="cert-label">出栏日期:</span>
            <span class="cert-value">${finish_date}</span>
          </div>` : ''}
          ${batch_image ? `
          <div>
            <img class="cert-image" src="${batch_image}" alt="批次实拍图" />
          </div>` : ''}

          <div class="cert-footer">
            <div class="cert-qrcode">
              ${qr_data_url ? `<img src="${qr_data_url}" alt="溯源二维码" />` : ''}
              <span>扫码核验</span>
            </div>
            <div class="cert-stamp">
              <div class="stamp-inner">
                <p>${farmer_name}</p>
                <p>质量合格章</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="trace-url">溯源链接：${trace_url}</div>
    </div>
  </body>
  </html>`

  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `生态养殖溯源合格证_${batch_code}_${export_date}.html`
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
  ElMessage.success('证书已下载（HTML）')
}
</script>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
}

.search-input {
  width: 320px;
}

.trace-content {
  margin-top: 20px;
}

.standard-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.trace-card :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  word-break: break-all;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.4;
}

.info-item .label {
  width: 70px;
  flex-shrink: 0;
  color: #909399;
}

.info-item .value {
  color: #303133;
  flex: 1;
  word-break: break-all;
}

.info-item .value.highlight {
  color: #409eff;
  font-weight: 600;
}

.card-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f2f6fc;
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.mb-4 {
  margin-bottom: 16px;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  background: #fff;
}

.cert-wrapper {
  padding: 10px 0;
}

.cert-container {
  padding: 30px;
  background: #fff;
  border: 4px double #67C23A;
  border-radius: 4px;
}

.cert-header {
  text-align: center;
  border-bottom: 2px solid #67C23A;
  padding-bottom: 20px;
  margin-bottom: 25px;
}

.cert-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 10px;
}

.cert-logo h3 {
  margin: 0;
  color: #67C23A;
  font-size: 22px;
  letter-spacing: 2px;
}

.cert-title {
  font-size: 14px;
  color: #909399;
  letter-spacing: 4px;
}

.cert-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.cert-row {
  display: flex;
  align-items: center;
  font-size: 15px;
}

.cert-label {
  color: #606266;
  width: 92px;
  font-weight: bold;
}

.cert-value {
  color: #303133;
  flex: 1;
}

.cert-value.code {
  font-family: monospace;
  background: #f4f4f5;
  padding: 2px 8px;
  border-radius: 4px;
  color: #e6a23c;
}

.cert-image-wrapper {
  margin-top: -6px;
}

.cert-image {
  width: 100%;
  max-height: 240px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid #f0f2f5;
}

.cert-footer {
  margin-top: 30px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-top: 20px;
  border-top: 1px dashed #dcdfe6;
}

.cert-qrcode {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.cert-qrcode img {
  width: 80px;
  height: 80px;
  border: 1px solid #f0f2f5;
  border-radius: 6px;
}

.cert-qrcode span {
  font-size: 12px;
  color: #909399;
}

.cert-stamp {
  width: 120px;
  height: 120px;
  border: 3px solid rgba(245, 108, 108, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: rotate(-15deg);
}

.stamp-inner {
  text-align: center;
  color: rgba(245, 108, 108, 0.8);
  font-weight: bold;
}

.stamp-inner p {
  margin: 0;
  font-size: 13px;
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .header-left {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    width: 100% !important;
  }
}
</style>
