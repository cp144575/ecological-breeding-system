/**
 * 文件功能：通用 CRUD 逻辑 Hook
 */
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { debounce } from 'lodash-es'
import { useDataRefresh } from './useDataRefresh'
import { format_date_time, format_date } from '@/utils/format'

// 导出格式化函数，方便非 CRUD 组件直接使用
export { format_date_time, format_date }

interface CRUDOptions {
  api_url: string
  refresh_signals?: string[]
  search_fields?: string[]
  on_success?: (type: 'create' | 'update' | 'delete') => void
  delete_msg?: string
  default_query?: Record<string, any>
}

export function useCRUD(options: CRUDOptions) {
  const loading = ref(false)
  const list = ref<any[]>([])
  const total = ref(0)
  
  const query_params = reactive({
    search: '',
    page: 1,
    page_size: 10,
    ...(options.default_query || {})
  })

  // 获取列表；silent 用于 WebSocket / 轮询触发的刷新，不盖整页 loading，列表更快「跟上」数据
  const get_list = async (opts?: { silent?: boolean }) => {
    const silent = opts?.silent === true
    if (!silent) loading.value = true
    try {
      const res: any = await request.get(options.api_url, { params: query_params })
      if (res.results) {
        list.value = res.results
        total.value = res.count
      } else {
        list.value = Array.isArray(res) ? res : []
        total.value = list.value.length
      }
    } catch (error: any) {
      console.error('Fetch error:', error)
      if (!silent) {
        ElMessage.error(error.response?.data?.detail || '获取数据失败')
      }
    } finally {
      if (!silent) loading.value = false
    }
  }

  // 分页切换
  const handle_page_change = (page: number) => {
    query_params.page = page
    get_list()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  // 搜索
  const debounced_search = debounce(() => {
    query_params.page = 1
    get_list()
  }, 400)

  watch(() => query_params.search, debounced_search)

  // 实时刷新（静默拉列表，目标：推送后约 3s 内界面与数据一致）
  if (options.refresh_signals) {
    useDataRefresh((_dataType: string) => {
      void get_list({ silent: true })
    }, options.refresh_signals)
  }

  // 删除
  const handle_delete = (id: number, confirm_text?: string) => {
    const msg = confirm_text || options.delete_msg || '确定要删除该记录吗？'
    ElMessageBox.confirm(msg, '提示', {
      type: 'warning'
    }).then(async () => {
      try {
        await request.delete(`${options.api_url}${id}/`)
        ElMessage.success('删除成功')
        get_list()
        options.on_success?.('delete')
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '删除失败')
      }
    })
  }

  onMounted(() => {
    // 允许组件在 mounted 后手动触发 get_list，避免默认自动触发可能导致的参数未就绪问题
    // 如果 options.default_query 中有 status 且组件会通过 v-model 绑定 status，
    // 可能会导致这里先发一次请求，然后 v-model 变化又发一次，或者顺序错乱。
    // 但作为通用 hook，默认行为还是应该加载。
    // 业务组件可以通过手动调用 get_list 来控制时机，或者忽略这里的初始调用结果。
    get_list()
  })

  // 文本高亮处理 (辅助 UI)
  const highlight_text = (text: string, keyword: string) => {
    if (!text) return ''
    if (!keyword) return text
    const escape_reg = (str: string) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const reg = new RegExp(`(${escape_reg(keyword)})`, 'gi')
    return text.toString().replace(reg, `<mark class="highlight-keyword">$1</mark>`)
  }

  return {
    loading,
    list,
    total,
    query_params,
    get_list,
    handle_page_change,
    handle_delete,
    highlight_text,
    format_date_time,
    format_date
  }
}
