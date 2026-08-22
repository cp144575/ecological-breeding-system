<template>
  <div class="public-trace-container">
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="error" class="error-state">
      <el-result icon="error" title="查询失败" :sub-title="error_msg">
        <template #extra>
          <el-button type="primary" @click="handle_back">返回首页</el-button>
        </template>
      </el-result>
    </div>

    <div v-else-if="trace_data" class="trace-content">
      <!-- 头部：溯源码与认证状态 -->
      <div class="header-card">
        <div class="trace-header">
          <div class="logo">
            <div class="logo-icon">
              <el-icon :size="32" color="#2d8a4e"><CircleCheckFilled /></el-icon>
            </div>
            <div class="logo-text">
              <h1>智慧农业溯源平台</h1>
              <div class="auth-badge">
                <el-icon :size="12"><Checked /></el-icon>
                <span>官方认证 · 数据加密存证</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="trace-code-section">
          <div class="code-label">产品溯源码</div>
          <div class="code-value-wrapper">
            <span class="code">{{ trace_data.trace_code }}</span>
            <el-tag size="small" effect="light" type="success" class="verify-tag">已核验</el-tag>
          </div>
        </div>
        
        <div class="header-stats">
          <div class="stat-item">
            <div class="stat-value">100%</div>
            <div class="stat-label">真实性</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <div class="stat-value">{{ trace_data.is_farmer_certified ? '已认证' : '核验中' }}</div>
            <div class="stat-label">主体资质</div>
          </div>
        </div>
      </div>

      <!-- 核心信息卡片容器 -->
      <div class="info-container">
        <!-- 牲畜基本信息 -->
        <div class="info-section">
          <div class="section-header">
            <div class="section-title">
              <el-icon><InfoFilled /></el-icon>
              <span>档案详情</span>
            </div>
          </div>
          <el-card shadow="never" class="standard-card info-card">
            <div class="animal-profile">
              <div class="image-wrapper">
                <el-image 
                  v-if="trace_data.batch_info?.image" 
                  :src="trace_data.batch_info.image" 
                  fit="cover" 
                  class="animal-image"
                  :preview-src-list="[trace_data.batch_info.image]"
                />
                <div v-else class="image-placeholder">
                  <el-icon><Picture /></el-icon>
                </div>
              </div>
              <div class="profile-details">
                <div class="animal-name">生态养殖档案</div>
                <div class="grid-info">
                  <div class="grid-item">
                    <span class="label">品种</span>
                    <span class="value">{{ trace_data.batch_info?.breed || '优质品种' }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">入栏日期</span>
                    <span class="value">{{ trace_data.batch_info?.entry_date || '-' }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">出栏日期</span>
                    <span class="value">{{ trace_data.batch_info?.finish_date || '-' }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="introduction-text" v-if="trace_data.batch_info?.introduction">
              {{ trace_data.batch_info.introduction }}
            </div>
          </el-card>
        </div>

        <!-- 产地环境 -->
        <div class="info-section">
          <div class="section-header">
            <div class="section-title">
              <el-icon><LocationFilled /></el-icon>
              <span>产地环境</span>
            </div>
          </div>
          <el-card shadow="never" class="standard-card info-card">
            <div class="location-info">
              <div class="farmer-header">
                <div class="farmer-avatar">{{ trace_data.farmer_name?.charAt(0) }}</div>
                <div class="farmer-meta">
                  <div class="farmer-name">{{ trace_data.farmer_name }}</div>
                  <div class="area-tag">
                    <el-icon><Place /></el-icon>
                    {{ trace_data.area_info?.area_name }}
                  </div>
                </div>
              </div>
              
              <div class="area-content" v-if="trace_data.area_info">
                <p class="area-description">{{ trace_data.area_info.description }}</p>
                <el-image 
                  v-if="trace_data.area_info.image" 
                  :src="trace_data.area_info.image" 
                  fit="cover" 
                  class="area-image"
                  :preview-src-list="[trace_data.area_info.image]"
                />
              </div>
            </div>
          </el-card>
        </div>

        <!-- 溯源历程 - 采用更精美的设计 -->
        <div class="info-section">
          <div class="section-header">
            <div class="section-title">
              <el-icon><List /></el-icon>
              <span>生命周期溯源</span>
            </div>
          </div>
          
          <div class="trace-tabs-wrapper">
            <el-tabs v-model="active_tab" class="custom-trace-tabs">
              <el-tab-pane name="feeding">
                <template #label>
                  <div class="tab-label">
                    <el-icon><Food /></el-icon>
                    <span>投喂</span>
                  </div>
                </template>
                <div class="timeline-container">
                  <el-timeline v-if="trace_data.feeding_history?.length">
                    <el-timeline-item
                      v-for="(item, index) in trace_data.feeding_history"
                      :key="index"
                      :timestamp="format_date_time(item.feeding_time, 'YYYY-MM-DD HH:mm')"
                      placement="top"
                      type="success"
                      size="large"
                    >
                      <div class="timeline-card">
                        <div class="card-title">{{ item.feed_name }}</div>
                        <div class="card-meta">
                          <span class="weight">投喂量：{{ item.feed_weight }}kg</span>
                        </div>
                      </div>
                    </el-timeline-item>
                  </el-timeline>
                  <el-empty v-else description="暂无记录" :image-size="60" />
                </div>
              </el-tab-pane>

              <el-tab-pane name="vaccine">
                <template #label>
                  <div class="tab-label">
                    <el-icon><FirstAidKit /></el-icon>
                    <span>防疫</span>
                  </div>
                </template>
                <div class="timeline-container">
                  <el-timeline v-if="trace_data.vaccination_history?.length">
                    <el-timeline-item
                      v-for="(item, index) in trace_data.vaccination_history"
                      :key="index"
                      :timestamp="item.vaccination_date"
                      placement="top"
                      type="primary"
                      size="large"
                    >
                      <div class="timeline-card">
                        <div class="card-title">{{ item.vaccine_name }}</div>
                        <div class="card-status">完成免疫接种</div>
                      </div>
                    </el-timeline-item>
                  </el-timeline>
                  <el-empty v-else description="暂无记录" :image-size="60" />
                </div>
              </el-tab-pane>

              <el-tab-pane name="disease">
                <template #label>
                  <div class="tab-label">
                    <el-icon><Odometer /></el-icon>
                    <span>健康</span>
                  </div>
                </template>
                <div class="timeline-container">
                  <el-timeline v-if="trace_data.disease_history?.length">
                    <el-timeline-item
                      v-for="(item, index) in trace_data.disease_history"
                      :key="index"
                      :timestamp="item.report_date"
                      placement="top"
                      :type="item.status_display === '已康复' ? 'success' : 'danger'"
                      size="large"
                    >
                      <div class="timeline-card">
                        <div class="card-title">{{ item.disease_name }}</div>
                        <div class="status-badge">
                          <el-tag size="small" :type="item.status_display === '已康复' ? 'success' : 'danger'">
                            {{ item.status_display }}
                          </el-tag>
                        </div>
                      </div>
                    </el-timeline-item>
                  </el-timeline>
                  <el-empty v-else description="暂无异常记录" :image-size="60" />
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>

      <!-- 底部信任背书 -->
      <div class="trust-footer">
        <div class="blockchain-badge">
          <el-icon><Link /></el-icon>
          <span>区块链加密存证 · 真实不可篡改</span>
        </div>
        <p class="copyright">© 2026 智慧农业溯源平台 提供技术支持</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：公开溯源详情页面 (支持微信、支付宝扫码访问)
 */
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { 
  CircleCheckFilled, 
  InfoFilled, 
  LocationFilled, 
  List, 
  Checked, 
  Picture, 
  Place, 
  Food, 
  FirstAidKit, 
  Odometer, 
  Link 
} from '@element-plus/icons-vue'
import { format_date_time } from '@/hooks/useCRUD'

const route = useRoute()
const router = useRouter()
const trace_code = route.params.code as string

const loading = ref(true)
const error = ref(false)
const error_msg = ref('')
const trace_data = ref<any>(null)
const active_tab = ref('feeding')

const fetch_trace_data = async () => {
  loading.value = true
  error.value = false
  try {
    // 使用直接 axios 请求，避免被全局拦截器重定向到登录页
    const res = await axios.get(`/api/traceability/public/${trace_code}/`)
    trace_data.value = res.data
  } catch (err: any) {
    error.value = true
    error_msg.value = err.response?.data?.detail || '溯源码无效或已过期'
  } finally {
    loading.value = false
  }
}

const handle_back = () => {
  router.push('/')
}

onMounted(() => {
  if (trace_code) {
    fetch_trace_data()
  } else {
    error.value = true
    error_msg.value = '未提供有效的溯源码'
    loading.value = false
  }
})
</script>

<style scoped>
.public-trace-container {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 12px;
  max-width: 600px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.loading-state {
  background: #fff;
  padding: 30px;
  border-radius: 20px;
}

/* 头部卡片 */
.header-card {
  background: linear-gradient(135deg, #2d8a4e 0%, #1b5e20 100%);
  border-radius: 20px;
  padding: 24px;
  color: #fff;
  margin-bottom: 20px;
  box-shadow: 0 10px 25px rgba(45, 138, 78, 0.25);
  position: relative;
  overflow: hidden;
}

.header-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.trace-header {
  margin-bottom: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  background: #fff;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.logo-text h1 {
  font-size: 20px;
  margin: 0;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.auth-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  opacity: 0.85;
  margin-top: 4px;
}

.trace-code-section {
  background: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(8px);
  padding: 16px;
  border-radius: 14px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.code-label {
  font-size: 12px;
  opacity: 0.7;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.code-value-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.code {
  font-family: "JetBrains Mono", monospace;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 1px;
}

.header-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  opacity: 0.7;
}

.stat-divider {
  width: 1px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
}

/* 内容区 */
.info-container {
  padding-bottom: 20px;
}

.info-section {
  margin-bottom: 24px;
}

.section-header {
  padding: 0 4px 12px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.section-title .el-icon {
  color: #2d8a4e;
  font-size: 18px;
}

.info-card {
  border-radius: 18px !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
}

/* 档案详情 */
.animal-profile {
  display: flex;
  gap: 16px;
}

.image-wrapper {
  width: 110px;
  height: 110px;
  border-radius: 14px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f1f5f9;
}

.animal-image {
  width: 100%;
  height: 100%;
  transition: transform 0.3s;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #cbd5e1;
}

.profile-details {
  flex: 1;
}

.animal-name {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 12px;
}

.grid-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.grid-item {
  display: flex;
  flex-direction: column;
}

.grid-item .label {
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 2px;
}

.grid-item .value {
  font-size: 13px;
  color: #334155;
  font-weight: 600;
}

.introduction-text {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

/* 产地环境 */
.farmer-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.farmer-avatar {
  width: 44px;
  height: 44px;
  background: #e2f2e7;
  color: #2d8a4e;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
}

.farmer-name {
  font-weight: 700;
  color: #1e293b;
  font-size: 15px;
}

.area-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.area-description {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  margin-bottom: 12px;
}

.area-image {
  width: 100%;
  height: 180px;
  border-radius: 14px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 溯源历程 */
.trace-tabs-wrapper {
  background: #fff;
  border-radius: 18px;
  padding: 4px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
}

.custom-trace-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
  border-bottom: 1px solid #f1f5f9;
}

.custom-trace-tabs :deep(.el-tabs__nav) {
  width: 100%;
  display: flex;
}

.custom-trace-tabs :deep(.el-tabs__item) {
  flex: 1;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 !important;
}

.tab-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  line-height: 1;
}

.tab-label .el-icon {
  font-size: 18px;
  margin-bottom: 2px;
}

.tab-label span {
  font-size: 12px;
  font-weight: 600;
}

.timeline-container {
  padding: 24px 16px;
  max-height: 400px;
  overflow-y: auto;
}

.timeline-card {
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 12px;
  border-left: 4px solid #2d8a4e;
}

.timeline-card .card-title {
  font-weight: 700;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
}

.timeline-card .card-meta {
  font-size: 12px;
  color: #64748b;
}

.timeline-card .card-status {
  font-size: 12px;
  color: #2d8a4e;
  font-weight: 600;
}

/* 底部 */
.trust-footer {
  text-align: center;
  padding: 30px 0 40px;
}

.blockchain-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
  font-weight: 500;
}

.blockchain-badge .el-icon {
  color: #2d8a4e;
}

.copyright {
  font-size: 11px;
  color: #94a3b8;
  margin: 0;
}

/* 滚动条美化 */
.timeline-container::-webkit-scrollbar {
  width: 4px;
}

.timeline-container::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 4px;
}

/* 动画 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.info-section {
  animation: fadeInUp 0.6s ease-out both;
}

.info-section:nth-child(1) { animation-delay: 0.1s; }
.info-section:nth-child(2) { animation-delay: 0.2s; }
.info-section:nth-child(3) { animation-delay: 0.3s; }
</style>
