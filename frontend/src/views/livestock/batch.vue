<template>
  <div class="page-container">
    <div class="header-actions">
      <div class="header-left">
        <h2>牲畜批次管理</h2>
        <el-input
          v-model="query_params.search"
          placeholder="搜索批次号或大类"
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
          <el-icon><Plus /></el-icon>新增批次
        </el-button>
      </div>
    </div>

    <el-card class="standard-card table-card" :body-style="{ padding: '0' }" v-loading="loading">
      <div class="responsive-grid">
        <div v-for="item in batch_list" :key="item.id" class="modern-card mobile-card">
          <div class="mobile-card-header">
            <div class="batch-header-left">
              <el-tag size="small" effect="plain">
                <span v-html="highlight_text(item.batch_code, query_params.search)"></span>
              </el-tag>
            </div>
            <el-tag :type="get_status_type(item.status)" size="small">
              {{ get_status_label(item.status) }}
            </el-tag>
          </div>

          <div class="mobile-card-content">
            <div class="info-item" v-if="item.image">
              <span class="label">实拍图：</span>
              <div class="value" style="flex: 1; margin-left: 10px;">
                <el-image
                  :src="item.image"
                  :preview-src-list="[item.image]"
                  fit="cover"
                  class="batch-thumb"
                  preview-teleported
                />
              </div>
            </div>

            <div class="info-item">
              <span class="label">大类/品种：</span>
              <span class="value">
                <span v-html="highlight_text(item.category_name || '', query_params.search)"></span>
                / {{ item.breed || '-' }}
              </span>
            </div>

            <div class="info-item">
              <span class="label">区域：</span>
              <span class="value">{{ item.area_name }}</span>
            </div>

            <div class="info-item" v-if="user_store.userInfo?.role === 'admin'">
              <span class="label">养殖户：</span>
              <span class="value">{{ item.farmer_name || '-' }}</span>
            </div>

            <div class="info-item">
              <span class="label">养殖数量：</span>
              <span class="value highlight">{{ item.quantity }}</span>
            </div>

            <div class="info-item">
              <span class="label">生长进度：</span>
              <div class="value" style="flex: 1; margin-left: 10px;">
                <el-progress
                  :percentage="Number(item.growth_progress || 0)"
                  :status="Number(item.growth_progress || 0) >= 90 ? 'exception' : (Number(item.growth_progress || 0) >= 80 ? 'warning' : 'success')"
                  :stroke-width="10"
                />
                <div style="margin-top: 6px; color: #909399; font-size: 12px; display: flex; justify-content: space-between; gap: 12px;">
                  <span>已养 {{ item.growth_days || 0 }} 天</span>
                  <span>周期 {{ item.standard_cycle || 0 }} 天</span>
                  <span v-if="item.expected_finish_date">预计出栏 {{ String(item.expected_finish_date).slice(0, 10) }}</span>
                </div>
              </div>
            </div>



            <div class="info-item">
              <span class="label">生态评分：</span>
              <div class="value" style="display: flex; align-items: center; gap: 8px;">
                <el-tooltip :content="`生态评分：${format_eco_score(item.eco_score)}星`" placement="top">
                  <el-rate :model-value="format_eco_score(item.eco_score)" disabled allow-half size="small" />
                </el-tooltip>
                <el-button link class="eco-rule-btn" @click="open_eco_panel(item)">规则</el-button>
              </div>
            </div>

            <div class="info-item" v-if="item.trace_code">
              <span class="label">溯源码：</span>
              <span class="value trace-code-mobile">{{ item.trace_code }}</span>
            </div>

            <div class="info-item" v-if="item.trace_code">
              <span class="label">溯源操作：</span>
              <div class="value" style="display: flex; gap: 10px; flex-wrap: wrap;">
                <el-button link class="btn-action-view" @click="copy_trace_link(item.trace_code)">复制链接</el-button>
              </div>
            </div>
          </div>

          <div class="mobile-card-footer table-ops">
            <el-button
              v-if="item.status === 'finished'"
              class="btn-action-view"
              link
              style="color: var(--primary-green) !important;"
              @click="show_certificate(item)"
            >
              合格证
            </el-button>

            <el-button class="btn-action-view" link @click="show_trace_timeline(item)">溯源</el-button>

            <el-button
              v-if="user_store.userInfo?.role !== 'admin'"
              class="btn-action-edit"
              link
              :disabled="!user_store.userInfo?.profile?.is_verified"
              @click="handle_edit(item)"
            >
              编辑
            </el-button>

            <el-button
              v-if="user_store.userInfo?.role !== 'admin' && item.status === 'active'"
              class="btn-action-edit"
              link
              style="color: var(--primary-green) !important;"
              :disabled="!user_store.userInfo?.profile?.is_verified"
              @click="handle_finish(item)"
            >
              出栏
            </el-button>

            <el-button
              class="btn-action-delete"
              link
              :disabled="user_store.userInfo?.role === 'farmer' && !user_store.userInfo?.profile?.is_verified"
              @click="handle_delete(item.id, `确定要删除批次 '${item.batch_code}' 吗？这将同时删除所有关联的生产记录！`)"
            >
              删除
            </el-button>
          </div>
        </div>
        <el-empty v-if="!batch_list.length" description="暂无批次记录" />
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

    <!-- 弹窗 -->
    <el-dialog :title="dialog_title" v-model="dialog_visible" width="650px" class="standard-dialog">
      <el-form :model="batch_form" label-width="100px" ref="form_ref" :rules="rules" label-position="top">
        <el-divider content-position="left">基本信息</el-divider>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="批次编号" prop="batch_code">
              <el-input v-model="batch_form.batch_code" placeholder="系统自动生成" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="展示图片">
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

        <el-divider content-position="left">养殖参数</el-divider>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="牲畜大类" prop="category">
              <el-select 
                v-model="batch_form.category" 
                placeholder="请选择大类（如：家禽、猪等）" 
                style="width: 100%"
                @change="handle_category_change"
              >
                <el-option 
                  v-for="item in categories" 
                  :key="item.id" 
                  :label="item.name" 
                  :value="item.id" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="养殖区域" prop="area">
              <el-select v-model="batch_form.area" placeholder="请选择" style="width: 100%">
                <el-option v-for="item in areas" :key="item.id" :label="item.area_name" :value="item.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="牲畜性别" prop="gender">
              <el-radio-group v-model="batch_form.gender">
                <el-radio-button label="公" />
                <el-radio-button label="母" />
                <el-radio-button label="混养" />
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="具体品种" prop="breed">
              <el-input v-model="batch_form.breed" placeholder="如：温氏三黄鸡、大白猪等" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="养殖数量" prop="quantity">
              <el-input-number v-model="batch_form.quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入栏日期" prop="entry_date">
              <el-date-picker
                v-model="batch_form.entry_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                :disabled-date="disable_future_dates"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24" v-if="batch_form.id">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="batch_form.status" style="width: 100%">
                <el-option label="养殖中" value="active" />
                <el-option label="已出栏" value="finished" />
                <el-option label="异常" value="abnormal" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="详细介绍" prop="introduction">
          <el-input v-model="batch_form.introduction" type="textarea" :rows="3" placeholder="简要描述牲畜的生长环境和特点..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialog_visible = false">取 消</el-button>
          <el-button class="btn-add" @click="handle_submit" :loading="submit_loading">
            {{ batch_form.id ? '保 存' : '立 即 创 建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 溯源时间轴抽屉 -->
    <el-drawer v-model="trace_visible" title="养殖溯源时间轴" size="520px" direction="rtl" class="trace-drawer">
      <div v-loading="trace_loading" class="trace-timeline-container">
        <el-timeline v-if="trace_data.length > 0">
          <el-timeline-item
            v-for="(activity, index) in trace_data"
            :key="index"
            :type="activity.type"
            :color="activity.color"
            :size="activity.size"
            :timestamp="activity.timestamp"
          >
            <div class="timeline-content">
              <h4>{{ activity.title }}</h4>
              <p>{{ activity.content }}</p>
            </div>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="暂无养殖记录" />
      </div>
    </el-drawer>

    <el-drawer v-model="eco_visible" title="生态合规评分" size="520px" direction="rtl" class="trace-drawer">
      <div v-loading="eco_loading" class="trace-timeline-container">
        <div v-if="eco_batch" class="eco-panel">
          <div class="eco-panel-header">
            <div class="eco-panel-title">
              <span class="code">{{ eco_batch.batch_code }}</span>
              <span class="name">{{ eco_batch.category_name }} / {{ eco_batch.breed || '-' }}</span>
            </div>
            <div class="eco-panel-score">
              <el-rate :model-value="eco_result.score" disabled allow-half />
              <span class="eco-score-text">{{ eco_result.score }} / 5</span>
            </div>
          </div>

          <el-divider />

          <el-table :data="eco_result.rules" border stripe size="small" style="width: 100%">
            <el-table-column prop="name" label="规则" min-width="160" />
            <el-table-column prop="status" label="满足情况" min-width="140" />
            <el-table-column prop="impact" label="影响" width="90" align="center" />
          </el-table>
        </div>
        <el-empty v-else description="请选择批次" />
      </div>
    </el-drawer>

    <!-- 可视化溯源合格证弹窗 -->
    <el-dialog
      title="生态养殖溯源合格证"
      v-model="cert_visible"
      width="500px"
      class="cert-dialog"
      destroy-on-close
    >
      <div class="cert-container" id="cert-content">
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
            <span class="cert-value">{{ current_batch?.category_name }} / {{ current_batch?.breed }}</span>
          </div>
          <div class="cert-row">
            <span class="cert-label">批次编号:</span>
            <span class="cert-value">{{ current_batch?.batch_code }}</span>
          </div>
          <div class="cert-row">
            <span class="cert-label">溯源编码:</span>
            <span class="cert-value code">{{ current_batch?.trace_code || '待生成' }}</span>
          </div>
          <div class="cert-row">
            <span class="cert-label">生态等级:</span>
            <span class="cert-value">
              <el-rate :model-value="format_eco_score(current_batch?.eco_score)" disabled allow-half />
              <span style="margin-left: 8px">{{ format_eco_score(current_batch?.eco_score) }} / 5</span>
            </span>
          </div>
          <div class="cert-row">
            <span class="cert-label">养殖区域:</span>
            <span class="cert-value">{{ current_batch?.area_name }}</span>
          </div>
          <div class="cert-row">
            <span class="cert-label">入栏日期:</span>
            <span class="cert-value">{{ current_batch?.entry_date }}</span>
          </div>
          <div v-if="current_batch?.status === 'finished'" class="cert-row">
            <span class="cert-label">出栏日期:</span>
            <span class="cert-value">{{ current_batch?.finish_date }}</span>
          </div>

          <div class="cert-footer">
            <div class="cert-qrcode">
              <template v-if="get_batch_trace_url(current_batch)">
                <QrcodeVue :value="get_batch_trace_url(current_batch)" :size="80" level="H" render-as="canvas" />
                <span>扫码核验</span>
              </template>
              <template v-else>
                <el-tag type="warning" effect="plain" size="small">溯源码生成中</el-tag>
                <span>请稍后刷新批次列表</span>
              </template>
            </div>
            <div class="cert-stamp">
              <div class="stamp-inner">
                <p>{{ current_batch?.farmer_name }}</p>
                <p>质量合格章</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="cert_visible = false">关闭</el-button>
        <el-button v-if="current_batch?.trace_code" @click="copy_trace_link(String(current_batch?.trace_code))">复制溯源链接</el-button>
        <el-button v-if="current_batch?.trace_code" @click="download_cert">下载证书</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：牲畜批次管理页面
 */
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { useUserStore } from '@/store/user'
import { useCRUD } from '@/hooks/useCRUD'
import { Plus, UploadFilled, Opportunity, Search } from '@element-plus/icons-vue'
import QrcodeVue from 'qrcode.vue'
import { validate_image_file } from '@/utils/image_upload'

const user_store = useUserStore()

// 合格证相关
const cert_visible = ref(false)
const current_batch = ref<any>(null)

const show_certificate = (row: any) => {
  current_batch.value = row
  cert_visible.value = true
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
            <span class="cert-value">${batch_breed}</span>
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

// 溯源时间轴相关
const trace_visible = ref(false)
const trace_loading = ref(false)
const trace_data = ref<any[]>([])

const eco_visible = ref(false)
const eco_loading = ref(false)
const eco_batch = ref<any>(null)
const eco_result = ref<{ score: number; rules: any[] }>({ score: 0, rules: [] })

const format_eco_score = (value: any) => {
  const numeric_value = Number(value)
  if (Number.isNaN(numeric_value)) return 0
  const clamped = Math.min(5, Math.max(0, numeric_value))
  return Math.round(clamped * 2) / 2
}

const open_eco_panel = async (row: any) => {
  eco_visible.value = true
  eco_loading.value = true
  eco_batch.value = row
  eco_result.value = { score: format_eco_score(row?.eco_score), rules: [] }

  try {
    const [vaccinations, diseases]: any = await Promise.all([
      request.get('/api/production/vaccination/', { params: { batch: row.id, page_size: 1 } }),
      request.get('/api/production/disease/', { params: { batch: row.id, page_size: 100 } })
    ])

    const vaccination_list = Array.isArray(vaccinations) ? vaccinations : (vaccinations.results || [])
    const disease_list = Array.isArray(diseases) ? diseases : (diseases.results || [])

    const has_vaccination = vaccination_list.length > 0
    const has_disease = disease_list.length > 0
    const has_unrecovered_disease = disease_list.some((item: any) => item.status !== 'recovered')

    const rules: any[] = []
    rules.push({ name: '基础分', status: '默认', impact: '+3' })
    rules.push({
      name: '防疫记录覆盖',
      status: has_vaccination ? `已记录（${vaccination_list.length}条）` : '未记录',
      impact: has_vaccination ? '+1' : '+0'
    })

    if (!has_disease) {
      rules.push({ name: '疾病记录情况', status: '无疾病记录', impact: '+1' })
    } else if (has_unrecovered_disease) {
      rules.push({ name: '疾病记录情况', status: '存在未康复/死亡记录', impact: '-1' })
    } else {
      rules.push({ name: '疾病记录情况', status: '存在疾病但已康复', impact: '+0' })
    }

    eco_result.value = {
      score: format_eco_score(row?.eco_score),
      rules
    }
  } catch (error) {
    console.error('获取生态评分明细失败:', error)
    ElMessage.error('获取生态评分明细失败')
  } finally {
    eco_loading.value = false
  }
}

const get_status_type = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'finished': return 'info'
    case 'abnormal': return 'danger'
    default: return ''
  }
}

const get_status_label = (status: string) => {
  switch (status) {
    case 'active': return '养殖中'
    case 'finished': return '已出栏'
    case 'abnormal': return '异常'
    default: return status
  }
}

const show_trace_timeline = async (row: any) => {
  trace_visible.value = true
  trace_loading.value = true
  trace_data.value = []
  
  try {
    const normalize_date_string = (value: any) => {
      const text_value = String(value || '')
      if (!text_value) return ''
      if (text_value.includes('T')) return text_value.split('T')[0]
      if (text_value.includes(' ')) return text_value.split(' ')[0]
      return text_value
    }

    const get_timestamp_value = (value: any) => {
      const date_value = Date.parse(String(value || ''))
      return Number.isNaN(date_value) ? 0 : date_value
    }

    // 聚合该批次的所有记录
    const [feedings, vaccinations, diseases]: any = await Promise.all([
      request.get('/api/production/feeding/', { params: { batch: row.id, page_size: 100 } }),
      request.get('/api/production/vaccination/', { params: { batch: row.id, page_size: 100 } }),
      request.get('/api/production/disease/', { params: { batch: row.id, page_size: 100 } })
    ])

    const timeline: any[] = []

    // 1. 入栏记录
    if (row.entry_date) {
      timeline.push({
        title: '入栏',
        content: `批次号 ${row.batch_code} 入栏，初始数量 ${row.quantity}`,
        timestamp: row.entry_date,
        type: 'primary',
        size: 'large',
        color: '#409EFF'
      })
    }

    // 2. 投喂记录
    const feeding_list = Array.isArray(feedings) ? feedings : (feedings.results || [])
    feeding_list.forEach((item: any) => {
      timeline.push({
        title: '投喂记录',
        content: `投喂 ${item.feed_name}，用量 ${item.feed_weight}${item.feed_unit || ''}`,
        timestamp: normalize_date_string(item.feeding_time),
        type: 'success',
        color: '#67C23A'
      })
    })

    // 3. 疫苗记录
    const vaccination_list = Array.isArray(vaccinations) ? vaccinations : (vaccinations.results || [])
    vaccination_list.forEach((item: any) => {
      timeline.push({
        title: '疫苗接种',
        content: `接种 ${item.vaccine_name}`,
        timestamp: item.vaccination_date,
        type: 'warning',
        color: '#E6A23C'
      })
    })

    // 4. 疾病记录
    const disease_list = Array.isArray(diseases) ? diseases : (diseases.results || [])
    disease_list.forEach((item: any) => {
      timeline.push({
        title: '异常上报',
        content: `发现异常: ${item.disease_name}，症状: ${item.symptoms}`,
        timestamp: item.report_date,
        type: 'danger',
        color: '#F56C6C'
      })
    })

    // 5. 出栏记录
    if (row.status === 'finished') {
      timeline.push({
        title: '已出栏',
        content: `批次 ${row.batch_code} 已顺利出栏，溯源码已生成`,
        timestamp: row.finish_date || row.expected_finish_date || '',
        type: 'info',
        size: 'large'
      })
    }

    // 按时间排序
    timeline.sort((a, b) => get_timestamp_value(b.timestamp) - get_timestamp_value(a.timestamp))
    trace_data.value = timeline

  } catch (error) {
    console.error('获取溯源数据失败:', error)
    ElMessage.error('获取溯源数据失败')
  } finally {
    trace_loading.value = false
  }
}

// 使用通用 CRUD Hook
const {
  loading,
  list: batch_list,
  total,
  query_params,
  get_list,
  handle_page_change,
  handle_delete,
  highlight_text
} = useCRUD({
  api_url: '/api/livestock/batch/',
  refresh_signals: ['livestockbatch'],
  delete_msg: '这将同时删除所有关联的生产记录！',
  default_query: {
    page_size: 9
  }
})

const areas = ref<any[]>([])
const categories = ref<any[]>([])
const submit_loading = ref(false)
const upload_progress = ref(0)
const dialog_visible = ref(false)
const dialog_title = ref('')
const form_ref = ref()
const image_preview = ref('')
const image_file = ref<File | null>(null)

const disable_future_dates = (time: Date) => {
  const today_end = new Date()
  today_end.setHours(23, 59, 59, 999)
  return time.getTime() > today_end.getTime()
}


const batch_form = reactive({
  id: null,
  batch_code: '',
  area: '',
  category: null,
  livestock_type: '',
  gender: '混养',
  breed: '',
  introduction: '',
  quantity: 10,
  entry_date: new Date().toISOString().split('T')[0],
  image: '',
  status: 'active'
})

const handle_category_change = (val: number) => {
  const category = categories.value.find(item => item.id === val)
  if (category) {
    batch_form.livestock_type = category.name
  }
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

    if (typeof image_preview.value === 'string' && image_preview.value.startsWith('blob:')) {
      URL.revokeObjectURL(image_preview.value)
    }
    image_file.value = raw_file
    image_preview.value = URL.createObjectURL(raw_file)
  })()
}

const get_trace_url = (code: string | undefined | null) => {
  if (!code) return ''
  // 构建公开溯源页面的 URL
  return `${window.location.origin}/public/trace/${code}`
}

const get_batch_trace_url = (batch_data: any) => {
  const trace_url = String(batch_data?.trace_url || '').trim()
  if (trace_url) {
    return trace_url
  }
  return get_trace_url(batch_data?.trace_code)
}

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

const rules = {
  area: [{ required: true, message: '请选择区域', trigger: 'change' }],
  category: [{ required: true, message: '请选择种类', trigger: 'change' }],
  entry_date: [{ required: true, message: '请选择入栏日期', trigger: 'change' }]
}

const get_areas = async () => {
  try {
    const res: any = await request.get('/api/livestock/area/')
    areas.value = Array.isArray(res) ? res : (res?.results || [])
  } catch (error) {
    console.error('Failed to fetch areas:', error)
  }
}

const get_categories = async () => {
  try {
    const res: any = await request.get('/api/livestock/category/')
    categories.value = Array.isArray(res) ? res : (res?.results || [])
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  }
}

const handle_add = () => {
  dialog_title.value = '新增批次'
  Object.assign(batch_form, {
    id: null,
    batch_code: '',
    area: '',
    category: null,
    livestock_type: '',
    gender: '混养',
    breed: '',
    introduction: '',
    quantity: 10,
    entry_date: new Date().toISOString().split('T')[0],
    image: ''
  })
  if (image_preview.value.startsWith('blob:')) {
    URL.revokeObjectURL(image_preview.value)
  }
  image_preview.value = ''
  image_file.value = null
  dialog_visible.value = true
}

const handle_edit = (row: any) => {
  dialog_title.value = '编辑批次'
  Object.assign(batch_form, row)
  if (image_preview.value.startsWith('blob:')) {
    URL.revokeObjectURL(image_preview.value)
  }
  image_preview.value = String(row?.image || '')
  image_file.value = null
  dialog_visible.value = true
}

const handle_finish = (row: any) => {
  ElMessageBox.confirm('确定将该批次标记为已出栏吗？', '提示', { type: 'success' }).then(async () => {
    await request.patch(`/api/livestock/batch/${row.id}/`, { status: 'finished' })
    ElMessage.success('操作成功')
    get_list()
  }).catch(() => {})
}

const handle_submit = async () => {
  await form_ref.value.validate(async (valid: boolean) => {
    if (valid) {
      submit_loading.value = true
      upload_progress.value = 0
      try {
        const formData = new FormData()
        formData.append('area', String(batch_form.area))
        formData.append('category', String(batch_form.category))
        formData.append('livestock_type', batch_form.livestock_type)
        formData.append('gender', batch_form.gender)
        formData.append('breed', batch_form.breed)
        formData.append('introduction', batch_form.introduction)
        formData.append('quantity', String(batch_form.quantity))
        formData.append('entry_date', batch_form.entry_date || '')
        formData.append('status', batch_form.status)
        if (image_file.value) {
          formData.append('image', image_file.value)
        }

        if (batch_form.id) {
          await request.put(`/api/livestock/batch/${batch_form.id}/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (evt: any) => {
              const total = evt?.total
              if (!total) return
              upload_progress.value = Math.min(99, Math.round((evt.loaded / total) * 100))
            }
          })
          ElMessage({ type: 'success', message: '修改成功', customClass: 'success-message' })
        } else {
          await request.post('/api/livestock/batch/', formData, {
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
  get_areas()
  get_categories()
})
</script>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1600px; /* Wider container for grid */
  margin: 0 auto;
}

/* ... existing styles ... */

.responsive-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  padding: 20px;
}

@media (min-width: 768px) {
  .responsive-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1200px) {
  .responsive-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1600px) {
  .responsive-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.modern-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.mobile-card-content {
  flex: 1; /* Push footer to bottom */
}

/* Overriding original mobile-card styles to fit grid */
.mobile-card {
  margin-bottom: 0; /* Let grid handle gap */
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

.code-text {
  font-family: Monaco, Consolas, monospace;
  font-weight: 600;
  color: #409eff;
}

.trace-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.trace-icons {
  display: flex;
  gap: 12px;
  font-size: 16px;
}

.hover-icon {
  cursor: pointer;
  transition: all 0.2s;
  color: #909399;
}

.hover-icon:hover {
  transform: scale(1.2);
}

.hover-icon.success:hover { color: #67c23a; }
.hover-icon.primary:hover { color: #409eff; }
.hover-icon.info:hover { color: #909399; }

.qr-preview {
  text-align: center;
  padding: 10px;
}

.qr-preview p {
  margin: 8px 0 0;
  font-size: 12px;
  color: #606266;
}

.sub-text {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.batch-thumb {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  cursor: zoom-in;
}

.status-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.progress-box {
  width: 100%;
  padding: 0 10px;
}

.progress-text {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

.trace-timeline-container {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px 20px;
}

.timeline-content h4 {
  margin: 0 0 8px 0;
  font-size: 15px;
  color: #303133;
}

.timeline-content p {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.mb-1 {
  margin-bottom: 4px;
}

.no-img {
  font-size: 30px;
  color: #dcdfe6;
}

.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: flex-end;
  background: #fff;
}

/* 合格证样式 */
.cert-container {
  padding: 30px;
  background: #fff;
  border: 4px double #67C23A;
  border-radius: 4px;
  position: relative;
  font-family: "Microsoft YaHei", sans-serif;
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
  width: 90px;
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
  position: relative;
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

@media print {
  body * {
    visibility: hidden;
  }
  #cert-content, #cert-content * {
    visibility: visible;
  }
  #cert-content {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
  }
}

.ml-2 {
  margin-left: 8px;
}

.status-tags {
  display: flex;
  align-items: center;
  justify-content: center;
}
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

.batch-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.batch-name {
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mobile-card-content {
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item .label {
  color: #909399;
  width: 80px;
  flex-shrink: 0;
}

.info-item .value {
  color: #303133;
}

.trace-code-mobile {
  font-family: monospace;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 2px 6px;
  border-radius: 4px;
}

.mobile-card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f2f5;
}

/* 弹窗样式 */
.batch-uploader {
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  width: 120px;
  height: 120px;
  overflow: hidden;
  transition: all 0.3s;
}

.batch-uploader:hover {
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

@media screen and (max-width: 768px) {
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
