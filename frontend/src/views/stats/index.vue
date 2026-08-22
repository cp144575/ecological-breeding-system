<template>
  <div class="page-container stats-page">
    <!-- 页面头部：统计汇总 -->
    <div class="stats-header mb-20">
      <div class="header-left">
        <h2 class="page-title">数据分析中心</h2>
        <p class="page-desc">全方位监测养殖状态、合规性及资源效率</p>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <el-alert
      v-if="user_store.userInfo?.role === 'farmer' && stats_data?.is_verified === false"
      type="warning"
      :closable="false"
      :title="stats_data?.message || '您的账户尚未通过实名认证，暂无法查看统计图表。'"
      class="mb-20"
      show-icon
    />
    <el-row
      :gutter="20"
      class="mb-20"
      v-if="stats_data && (user_store.userInfo?.role === 'admin' || user_store.userInfo?.role === 'farmer') && stats_data?.is_verified !== false"
    >
      <el-col :span="6" :xs="12" v-for="item in display_stat_entries" :key="item.key">
        <el-card shadow="hover" class="metric-card">
          <div class="metric-content">
            <div class="metric-icon" :class="item.key">
              <el-icon><component :is="stat_icons[item.key] || List" /></el-icon>
            </div>
            <div class="metric-info">
              <div class="metric-label">{{ stat_labels[item.key] || item.key }}</div>
              <div class="metric-value">{{ format_stat_value(item.key, item.value) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <!-- 图表区域 -->
    <el-row
      :gutter="20"
      v-if="stats_data && (user_store.userInfo?.role === 'admin' || user_store.userInfo?.role === 'farmer') && stats_data?.is_verified !== false"
    >
      <el-col :span="trend_span" :xs="24" class="mb-20">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="title">{{ trend_title }}</span>
              <el-tag size="small">近30日</el-tag>
            </div>
          </template>
          <div ref="trend_ref" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col v-if="user_store.userInfo?.role === 'farmer'" :span="10" :xs="24" class="mb-20">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span class="title">{{ secondary_title }}</span>
            </div>
          </template>
          <el-empty
            v-if="!stats_data?.feed_stock_dist || stats_data.feed_stock_dist.length === 0"
            description="暂无饲料库存数据"
          />
          <div v-else ref="secondary_ref" class="chart-container pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
/**
 * 文件功能：数据统计分析页面
 * 提供深度的数据可视化，包括趋势分析、结构分布和综合评价雷达
 */
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import request from '@/utils/request'
import { useUserStore } from '@/store/user'
import { 
  List, Sugar, UserFilled, Warning, Checked
} from '@element-plus/icons-vue'

const user_store = useUserStore()
const stats_data = ref<any>(null)

// 图表引用
const trend_ref = ref<HTMLElement | null>(null)
const secondary_ref = ref<HTMLElement | null>(null)

let charts: echarts.ECharts[] = []

const role = computed(() => user_store.userInfo?.role)

const trend_span = computed(() => {
  return role.value === 'farmer' ? 14 : 24
})

// 统计配置
const stat_labels = computed<Record<string, string>>(() => {
  if (role.value === 'admin') {
    const labels: Record<string, string> = {
      farmer_count: '养殖户数',
      active_batch_count: '在养批次',
      pending_disease_count: '待处理疾病',
      vaccination_coverage_rate: '防疫覆盖率',
    }

    return labels
  }

  if (role.value === 'farmer') {
    const labels: Record<string, string> = {
      my_active_batch_count: '我的在养批次',
      pending_vaccination_batch_count: '待接种批次',
      low_stock_feed_count: '低库存饲料',
    }

    return labels
  }

  return {}
})

const stat_icons = computed<Record<string, any>>(() => {
  if (role.value === 'admin') {
    const icons: Record<string, any> = {
      farmer_count: UserFilled,
      active_batch_count: List,
      pending_disease_count: Warning,
      vaccination_coverage_rate: Checked,
    }

    return icons
  }

  if (role.value === 'farmer') {
    const icons: Record<string, any> = {
      my_active_batch_count: List,
      pending_vaccination_batch_count: Checked,
      low_stock_feed_count: Sugar,
    }

    return icons
  }

  return {}
})

const display_stats = computed<Record<string, any>>(() => {
  if (!stats_data.value?.base_stats || typeof stats_data.value.base_stats !== 'object') return {}
  return stats_data.value.base_stats
})

const display_stat_entries = computed(() => {
  return Object.entries(display_stats.value).map(([key, value]) => ({ key, value }))
})

const trend_title = computed(() => {
  if (role.value === 'admin') return '疾病上报趋势'
  if (role.value === 'farmer') return '投喂量趋势'
  return ''
})

const secondary_title = computed(() => {
  if (role.value === 'farmer') return '饲料储备结构'
  return ''
})

const format_stat_value = (key: string, val: any) => {
  if (val === null || val === undefined) return '-'
  if (key === 'vaccination_coverage_rate') return `${val}%`
  return val
}

const load_stats = async () => {
  try {
    if (!user_store.userInfo && user_store.token) {
      await user_store.getUserInfo()
    }

    if (user_store.userInfo?.role !== 'admin' && user_store.userInfo?.role !== 'farmer') {
      stats_data.value = null
      return
    }

    const endpoint = user_store.userInfo?.role === 'admin'
      ? '/api/stats/admin/dashboard/'
      : '/api/stats/farmer/dashboard/'
    
    const res: any = await request.get(endpoint)
    stats_data.value = res
    await nextTick()
    init_charts()
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

const init_charts = () => {
  // 清除旧图表
  charts.forEach(chart => chart.dispose())
  charts = []

  if (trend_ref.value) {
    const trend_data = role.value === 'admin' ? stats_data.value?.disease_trend : stats_data.value?.feeding_trend
    if (trend_data?.dates?.length) {
      const chart = echarts.init(trend_ref.value)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: trend_data.dates },
        yAxis: { type: 'value', minInterval: 1 },
        series: [
          {
            name: role.value === 'admin' ? '疾病上报' : '投喂量(kg)',
            type: 'line',
            smooth: true,
            data: trend_data.counts,
            areaStyle: { opacity: 0.1 },
            itemStyle: { color: role.value === 'admin' ? '#f56c6c' : '#409eff' },
          },
        ],
      })
      charts.push(chart)
    }
  }

  if (secondary_ref.value) {
    if (role.value === 'farmer' && stats_data.value?.feed_stock_dist) {
      const chart = echarts.init(secondary_ref.value)
      chart.setOption({
        textStyle: {
          color: '#303133',
          fontFamily: 'Microsoft YaHei, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif',
          fontSize: 12,
        },
        tooltip: { trigger: 'item' },
        legend: {
          type: 'scroll',
          bottom: 0,
          left: 'center',
          pageButtonGap: 6,
          pageButtonItemGap: 4,
          textStyle: {
            color: '#303133',
            fontSize: 12,
          },
        },
        series: [
          {
            type: 'pie',
            left: 16,
            right: 16,
            top: 12,
            bottom: 56,
            radius: '70%',
            center: ['50%', '42%'],
            avoidLabelOverlap: true,
            label: {
              show: true,
              color: '#303133',
              position: 'outside',
              alignTo: 'edge',
              edgeDistance: 10,
              bleedMargin: 8,
              distanceToLabelLine: 4,
              width: 92,
              overflow: 'break',
              lineHeight: 16,
              formatter: '{b}\n{d}%',
            },
            labelLine: {
              show: true,
              length: 12,
              length2: 10,
              lineStyle: {
                color: '#909399',
              },
            },
            data: stats_data.value.feed_stock_dist,
            emphasis: {
              itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' },
            },
          },
        ],
      })
      charts.push(chart)
    }
  }
}

// 响应式调整
const handle_resize = () => {
  charts.forEach(chart => chart.resize())
}

onMounted(() => {
  load_stats()
  window.addEventListener('resize', handle_resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handle_resize)
})
</script>

<style scoped lang="scss">
.stats-page {
  .mb-20 { margin-bottom: 20px; }
  
  .stats-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .page-title { margin: 0; font-size: 24px; color: #303133; }
    .page-desc { margin: 5px 0 0; color: #909399; font-size: 14px; }
  }

  .metric-card {
    border: none;
    border-radius: 12px;

    :deep(.el-card__body) {
      padding: 20px;
    }

    .metric-content {
      display: flex;
      align-items: center;
      gap: 14px;
      min-height: 48px;
    }

    .metric-icon {
      width: clamp(42px, 4vw, 48px);
      height: clamp(42px, 4vw, 48px);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      font-size: clamp(20px, 2vw, 24px);
      background: rgba(64, 158, 255, 0.1);
      color: #409eff;

      &.my_active_batch_count,
      &.active_batch_count {
        background: rgba(64, 158, 255, 0.1);
        color: #409eff;
      }

      &.pending_vaccination_batch_count {
        background: rgba(230, 162, 60, 0.1);
        color: #e6a23c;
      }

      &.low_stock_feed_count,
      &.pending_disease_count {
        background: rgba(245, 108, 108, 0.1);
        color: #f56c6c;
      }

      &.vaccination_coverage_rate {
        background: rgba(103, 194, 58, 0.1);
        color: #67c23a;
      }

      &.farmer_count {
        background: rgba(144, 147, 153, 0.1);
        color: #909399;
      }
    }

    .metric-info {
      min-width: 0;
      flex: 1;

      .metric-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 4px;
        line-height: 1.25;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .metric-value {
        font-size: clamp(22px, 2.2vw, 28px);
        font-weight: bold;
        color: #303133;
        line-height: 1.1;
      }
    }
  }

  @media (max-width: 768px) {
    .metric-card {
      :deep(.el-card__body) {
        padding: 16px;
      }

      .metric-content {
        gap: 12px;
        min-height: 44px;
      }

      .metric-info {
        .metric-label {
          font-size: 13px;
        }

        .metric-value {
          font-size: 22px;
        }
      }
    }
  }

  .chart-container {
    height: 300px;
    &.radar-chart { height: 350px; }
    &.pie-chart-container { height: 340px; }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    .title { font-weight: bold; font-size: 16px; }
  }

  .vaccine-stats {
    text-align: center;
    padding: 10px 0;
    .progress-box {
      margin-bottom: 20px;
      .progress-label { font-size: 14px; color: #909399; margin-top: 10px; }
    }
    .detail-list {
      .detail-item {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f5f7fa;
        font-size: 14px;
        color: #606266;
        &:last-child { border-bottom: none; }
        .val { 
          font-weight: bold; 
          &.success { color: #67c23a; }
          &.warning { color: #e6a23c; }
        }
      }
    }
  }
}
</style>
