/**
 * 文件功能：WebSocket 实时刷新
 * 目标：正常连上 WS 时亚秒级更新；断线时靠轮询在约 3s 内补偿（见 POLL_MS）
 */
import { onMounted, onUnmounted } from 'vue'
import { throttle } from 'lodash-es'
import { wsService } from '@/utils/websocket'

/** 推送合并窗口：略大于后端可能的双发（视图 + 信号），避免多余 HTTP */
const WS_THROTTLE_MS = 120

/** WebSocket 不可用时轮询间隔（保证最坏情况下约 3s 内能拉到新数据） */
const POLL_MS = 2800

/** 首屏若 WS 迟迟连不上，单次补偿拉取（避免干等第一轮轮询） */
const WS_DOWN_KICKOFF_MS = 1200

export function useDataRefresh(
  callback: (dataType: string) => void,
  targetTypes: string[] = ['all']
) {
  const throttledRun = throttle(callback, WS_THROTTLE_MS, { leading: true, trailing: true })

  let pollingTimer: ReturnType<typeof setInterval> | null = null
  let kickoffTimer: ReturnType<typeof setTimeout> | null = null

  const handler = (data: any) => {
    if (data.type !== 'refresh') return
    const { data_type } = data
    if (targetTypes.includes('all') || targetTypes.includes(data_type)) {
      throttledRun(data_type)
    }
  }

  const startPolling = () => {
    stopPolling()
    pollingTimer = setInterval(() => {
      if (!wsService.isConnected()) {
        callback('polling')
      }
    }, POLL_MS)
  }

  const stopPolling = () => {
    if (pollingTimer) {
      clearInterval(pollingTimer)
      pollingTimer = null
    }
    if (kickoffTimer) {
      clearTimeout(kickoffTimer)
      kickoffTimer = null
    }
  }

  onMounted(() => {
    wsService.connect()
    wsService.subscribe(handler)
    startPolling()
    kickoffTimer = setTimeout(() => {
      kickoffTimer = null
      if (!wsService.isConnected()) {
        callback('polling')
      }
    }, WS_DOWN_KICKOFF_MS)
  })

  onUnmounted(() => {
    throttledRun.cancel()
    wsService.unsubscribe(handler)
    stopPolling()
  })

  return {}
}
