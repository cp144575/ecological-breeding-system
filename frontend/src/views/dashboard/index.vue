<template>
  <div class="page-container dashboard-page">
    <!-- 中间区域：业务概览与预警 -->
    <el-row :gutter="20" class="main-content-row">
      <el-col :span="24" :xs="24">
        <el-row :gutter="20">
          <!-- 养殖进度预警 -->
          <el-col :span="12" :xs="24" class="mb-20">
            <el-card shadow="hover" class="info-card standard-card">
              <template #header>
                <div class="card-header">
                  <div class="title-wrapper">
                    <el-icon class="header-icon warning"><AlarmClock /></el-icon>
                    <span class="title">生长进度预警</span>
                  </div>
                  <el-tag size="small" type="warning">即将出栏</el-tag>
                </div>
              </template>
              <div v-loading="loading_batches" class="info-list">
                <div v-for="item in upcoming_batches" :key="item.id" class="info-item-box">
                  <div class="info-main">
                    <div class="item-title">{{ item.name }} ({{ item.batch_code }})</div>
                    <el-progress 
                      :percentage="item.growth_progress" 
                      :status="item.growth_progress >= 90 ? 'exception' : 'warning'"
                      :stroke-width="10"
                    />
                  </div>
                  <div class="item-side">
                    <div class="days-text">已养 {{ item.growth_days }} 天</div>
                    <div class="target-text">周期 {{ item.standard_cycle }} 天</div>
                  </div>
                </div>
                <el-empty v-if="upcoming_batches.length === 0" :image-size="60" description="暂无预警批次" />
              </div>
            </el-card>
          </el-col>

          <!-- 近期防疫任务 -->
          <el-col :span="12" :xs="24" class="mb-20">
            <el-card shadow="hover" class="info-card standard-card">
              <template #header>
                <div class="card-header">
                  <div class="title-wrapper">
                    <el-icon class="header-icon primary"><Checked /></el-icon>
                    <span class="title">智能待办/预警中心</span>
                  </div>
                  <el-button link type="primary" @click="fetch_todo_alerts">刷新</el-button>
                </div>
              </template>
              <div v-loading="loading_todos" class="info-list">
                <div v-for="item in todo_alerts" :key="item.key" class="info-item-box task-item">
                  <div class="task-icon" :class="item.level">
                    <el-icon><component :is="item.icon" /></el-icon>
                  </div>
                  <div class="task-info">
                    <div class="task-title">{{ item.title }}</div>
                    <div class="task-desc">{{ item.description }}</div>
                  </div>
                  <el-button v-if="item.action" link type="primary" @click="$router.push(item.action)">去处理</el-button>
                </div>
                <el-empty v-if="todo_alerts.length === 0" :image-size="60" description="暂无待办任务" />
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 生态合规性简报 (针对养殖户) -->
        <el-card shadow="hover" class="compliance-card standard-card" v-if="user_store.userInfo?.role === 'farmer'">
          <template #header>
            <div class="card-header">
              <div class="title-wrapper">
                <el-icon class="header-icon success"><Check /></el-icon>
                <span class="title">生态养殖合规概览</span>
              </div>
            </div>
          </template>
          <div class="compliance-content" v-if="stats_data">
            <div class="compliance-item">
              <div class="label">防疫覆盖率</div>
              <div class="value-box">
                <el-progress type="circle" :percentage="vaccination_coverage_rate" :width="72" :color="customColors" />
              </div>
            </div>
            <div class="compliance-item">
              <div class="label">平均生态星级</div>
              <div class="value-box star-box">
                <el-rate v-model="avg_eco_score" disabled show-score text-color="#ff9900" />
                <span class="hint">基于存栏批次自动计算</span>
              </div>
            </div>
            <div class="compliance-item">
              <div class="label">健康预警</div>
              <div class="value-box">
                <span class="status-text" :class="disease_total_count > 0 ? 'danger' : 'safe'">
                  {{ disease_total_count > 0 ? '存在异常上报' : '环境运行平稳' }}
                </span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：系统首页仪表盘 (养殖户视角优化)
 * 整合统计指标、业务预警、快捷入口与动态中心
 */
import { ref, onMounted, computed } from 'vue'
import request from '@/utils/request'
import { 
  AlarmClock, Checked,
  Check, Warning
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const user_store = useUserStore()
const stats_data = ref<any>(null)

// 预警与待办数据
const upcoming_batches = ref<any[]>([])
const todo_alerts = ref<any[]>([])
const loading_batches = ref(false)
const loading_todos = ref(false)

const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 },
]

const avg_eco_score = computed(() => {
  return stats_data.value?.avg_eco_score || 0
})

const vaccination_coverage_rate = computed(() => {
  const base_stats = stats_data.value?.base_stats
  const active_batch_count = Number(base_stats?.my_active_batch_count ?? base_stats?.active_batch_count ?? 0)
  const pending_vaccination_batch_count = Number(base_stats?.pending_vaccination_batch_count ?? 0)
  if (active_batch_count <= 0) return 0
  const vaccinated_batch_count = Math.max(active_batch_count - pending_vaccination_batch_count, 0)
  return Math.min(100, Math.max(0, Math.round((vaccinated_batch_count / active_batch_count) * 100)))
})

const disease_total_count = computed(() => {
  const counts = stats_data.value?.disease_trend?.counts
  if (!Array.isArray(counts)) return 0
  return counts.reduce((total: number, current: number) => total + current, 0)
})

// 获取统计数据
const fetch_stats = async () => {
  try {
    if (!user_store.userInfo && user_store.token) {
      await user_store.getUserInfo()
    }

    const res: any = await request.get('/api/stats/farmer/dashboard/')
    stats_data.value = res
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

// 获取预警批次
const fetch_upcoming_batches = async () => {
  loading_batches.value = true
  try {
    const res: any = await request.get('/api/livestock/batch/', { 
      params: { status: 'active', page_size: 50 } 
    })
    const list = Array.isArray(res) ? res : (res.results || [])
    upcoming_batches.value = list
      .filter((item: any) => Number(item.growth_progress) >= 80)
      .sort((a: any, b: any) => Number(b.growth_progress) - Number(a.growth_progress))
      .slice(0, 5)
  } catch (error) {
    console.error('获取预警批次失败:', error)
  } finally {
    loading_batches.value = false
  }
}

// 获取待办防疫
const fetch_todo_alerts = async () => {
  loading_todos.value = true
  try {
    const now = new Date()
    const in_days = (date_text: string, days: number) => {
      const parsed = Date.parse(date_text)
      if (Number.isNaN(parsed)) return false
      const delta = parsed - now.getTime()
      return delta <= days * 24 * 60 * 60 * 1000
    }

    const [batch_res, vaccination_res, disease_pending_res, disease_treating_res]: any = await Promise.all([
      request.get('/api/livestock/batch/', { params: { status: 'active', page_size: 50 } }),
      request.get('/api/production/vaccination/', { params: { page_size: 200 } }),
      request.get('/api/production/disease/', { params: { status: 'pending', page_size: 20 } }),
      request.get('/api/production/disease/', { params: { status: 'treating', page_size: 20 } })
    ])

    const active_batches = Array.isArray(batch_res) ? batch_res : (batch_res.results || [])
    const vaccination_list = Array.isArray(vaccination_res) ? vaccination_res : (vaccination_res.results || [])
    const disease_pending_list = Array.isArray(disease_pending_res) ? disease_pending_res : (disease_pending_res.results || [])
    const disease_treating_list = Array.isArray(disease_treating_res) ? disease_treating_res : (disease_treating_res.results || [])

    const vaccinated_batch_ids = new Set<number>()
    vaccination_list.forEach((item: any) => {
      if (typeof item.batch === 'number') vaccinated_batch_ids.add(item.batch)
    })

    const items: any[] = []

    disease_pending_list.slice(0, 5).forEach((item: any) => {
      items.push({
        key: `disease_pending_${item.id}`,
        level: 'danger',
        icon: Warning,
        title: `疾病待处理：${item.disease_name}`,
        description: `批次 ${item.batch_code || item.batch} · ${item.report_date}`,
        action: '/production/disease'
      })
    })

    disease_treating_list.slice(0, 5).forEach((item: any) => {
      items.push({
        key: `disease_treating_${item.id}`,
        level: 'warning',
        icon: AlarmClock,
        title: `疾病治疗中：${item.disease_name}`,
        description: `批次 ${item.batch_code || item.batch} · ${item.report_date}`,
        action: '/production/disease'
      })
    })

    const due_vaccinations = vaccination_list.filter((item: any) => {
      if (!item.next_vaccination_date) return false
      return in_days(item.next_vaccination_date, 7)
    })
    due_vaccinations.slice(0, 5).forEach((item: any) => {
      items.push({
        key: `vaccination_due_${item.id}`,
        level: 'warning',
        icon: Checked,
        title: `即将接种：${item.vaccine_name}`,
        description: `批次 ${item.batch_code || item.batch} · 下次 ${item.next_vaccination_date}`,
        action: '/production/vaccination'
      })
    })

    const missing_vaccination_batches = active_batches.filter((b: any) => !vaccinated_batch_ids.has(b.id))
    missing_vaccination_batches.slice(0, 5).forEach((b: any) => {
      items.push({
        key: `vaccination_missing_${b.id}`,
        level: 'info',
        icon: Checked,
        title: '补录防疫记录',
        description: `批次 ${b.batch_code} 尚无疫苗接种记录`,
        action: '/production/vaccination'
      })
    })

    const low_eco_batches = active_batches.filter((b: any) => Number(b.eco_score) > 0 && Number(b.eco_score) < 4)
    low_eco_batches.slice(0, 5).forEach((b: any) => {
      items.push({
        key: `eco_low_${b.id}`,
        level: 'info',
        icon: Check,
        title: '提升生态星级',
        description: `批次 ${b.batch_code} 当前 ${b.eco_score} 星`,
        action: '/livestock/batch'
      })
    })

    const level_rank: Record<string, number> = { danger: 0, warning: 1, info: 2, success: 3 }
    items.sort((a, b) => (level_rank[a.level] ?? 9) - (level_rank[b.level] ?? 9))

    todo_alerts.value = items
  } catch (error) {
    console.error('获取待办与预警失败:', error)
  } finally {
    loading_todos.value = false
  }
}

onMounted(() => {
  fetch_stats()
  fetch_upcoming_batches()
  fetch_todo_alerts()
})
</script>

<style scoped lang="scss">
.dashboard-page {
  .mb-20 { margin-bottom: 20px; }

  .main-content-row {
    .standard-card {
      border-radius: 12px;
      border: none;
      height: 100%;
      :deep(.el-card__header) {
        border-bottom: 1px solid #f0f2f5;
        padding: 15px 20px;
      }
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      .title-wrapper {
        display: flex;
        align-items: center;
        .header-icon {
          margin-right: 8px;
          font-size: 18px;
          &.warning { color: #e6a23c; }
          &.primary { color: #409eff; }
          &.success { color: #67c23a; }
        }
        .title { font-weight: bold; font-size: 16px; }
      }
    }

    .info-list {
      height: 280px;
      overflow-y: auto;
      .info-item-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f5f7fa;
        &:last-child { border-bottom: none; }
        
        .info-main {
          flex: 1;
          margin-right: 20px;
          .item-title { font-size: 14px; color: #303133; margin-bottom: 8px; }
        }
        
        .item-side {
          text-align: right;
          .days-text { font-size: 13px; color: #606266; font-weight: 500; }
          .target-text { font-size: 11px; color: #909399; margin-top: 2px; }
        }

        &.task-item {
          .task-icon {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: #f0f7ff;
            color: #409eff;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;

            &.danger {
              background: #fef0f0;
              color: #f56c6c;
            }
            &.warning {
              background: #fdf6ec;
              color: #e6a23c;
            }
            &.info {
              background: #f0f7ff;
              color: #409eff;
            }
            &.success {
              background: #f0f9eb;
              color: #67c23a;
            }
          }
          .task-info {
            flex: 1;
            .task-title { font-size: 14px; color: #303133; font-weight: 500; }
            .task-desc { font-size: 12px; color: #909399; margin-top: 4px; }
          }
          .task-time { font-size: 12px; color: #c0c4cc; }
        }
      }
    }

    .compliance-card {
      height: auto;

      :deep(.el-card__body) {
        padding: 0;
      }

      .compliance-content {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        padding: 12px 16px;
        .compliance-item {
          text-align: center;
          background: #fbfcfe;
          border: 1px solid #f0f2f5;
          border-radius: 12px;
          padding: 12px;

          .label { font-size: 13px; color: #909399; margin-bottom: 10px; }
          .value-box {
            min-height: 76px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            &.star-box { gap: 10px; }
            .hint { font-size: 11px; color: #c0c4cc; }
            .status-text {
              font-size: 16px;
              font-weight: bold;
              &.safe { color: #67c23a; }
              &.danger { color: #f56c6c; }
            }
          }
        }
      }

      @media (max-width: 992px) {
        .compliance-content {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }

      @media (max-width: 640px) {
        .compliance-content {
          grid-template-columns: 1fr;
          padding: 10px 12px;
        }
      }
    }

  }
}
</style>
