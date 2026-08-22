import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'
import request from '@/utils/request'

type CertTabKey = '0' | '1' | '2'

type CertListItem = any

type CertTabState = {
  list: CertListItem[]
  total: number
  page: number
  loading: boolean
  loaded: boolean
  error_message: string
}

const create_tab_state = (): CertTabState => ({
  list: [],
  total: 0,
  page: 1,
  loading: false,
  loaded: false,
  error_message: ''
})

const tab_keys: CertTabKey[] = ['0', '1', '2']

export const useCertManageStore = defineStore('cert_manage', () => {
  const active_tab = ref<CertTabKey>('0')
  const search_keyword = ref('')
  const page_size = ref(8)

  const tabs = reactive<Record<CertTabKey, CertTabState>>({
    '0': create_tab_state(),
    '1': create_tab_state(),
    '2': create_tab_state()
  })

  const request_seq = reactive<Record<CertTabKey, number>>({
    '0': 0,
    '1': 0,
    '2': 0
  })

  const abort_controller_by_tab: Record<CertTabKey, AbortController | null> = {
    '0': null,
    '1': null,
    '2': null
  }

  const active_state = computed(() => tabs[active_tab.value])

  const abort_tab_request = (tab_key: CertTabKey) => {
    const controller = abort_controller_by_tab[tab_key]
    if (controller) {
      controller.abort()
      abort_controller_by_tab[tab_key] = null
    }
  }

  const abort_all_requests = () => {
    for (const tab_key of tab_keys) {
      abort_tab_request(tab_key)
    }
  }

  const invalidate_all_tabs = () => {
    for (const tab_key of tab_keys) {
      tabs[tab_key].loaded = false
      tabs[tab_key].error_message = ''
      tabs[tab_key].page = 1
    }
  }

  const set_active_tab = (tab_key: CertTabKey) => {
    active_tab.value = tab_key
  }

  const set_search_keyword = (keyword: string) => {
    search_keyword.value = keyword
  }

  const set_active_page = (page: number) => {
    tabs[active_tab.value].page = page
  }

  const fetch_tab = async (tab_key: CertTabKey, options?: { force?: boolean; page?: number }) => {
    const tab_state = tabs[tab_key]
    const force = Boolean(options?.force)
    const page = typeof options?.page === 'number' ? options.page : tab_state.page

    if (!force && tab_state.loaded && tab_state.page === page) {
      return
    }

    abort_tab_request(tab_key)
    tab_state.loading = true
    tab_state.error_message = ''
    tab_state.page = page

    const controller = new AbortController()
    abort_controller_by_tab[tab_key] = controller

    request_seq[tab_key] += 1
    const seq = request_seq[tab_key]

    try {
      const res: any = await request.get('/api/users/cert/', {
        params: {
          status: tab_key,
          search: search_keyword.value,
          page: tab_state.page,
          page_size: page_size.value
        },
        signal: controller.signal
      })

      if (request_seq[tab_key] !== seq) {
        return
      }

      if (res?.results) {
        tab_state.list = Array.isArray(res.results) ? res.results : []
        tab_state.total = Number(res.count || 0)
      } else {
        tab_state.list = Array.isArray(res) ? res : []
        tab_state.total = tab_state.list.length
      }

      tab_state.loaded = true
    } catch (error: any) {
      if (error?.code === 'ERR_CANCELED' || error?.name === 'CanceledError') {
        return
      }
      tab_state.error_message = String(error?.response?.data?.detail || '获取数据失败')
    } finally {
      if (request_seq[tab_key] === seq) {
        tab_state.loading = false
      }
    }
  }

  const ensure_active_loaded = async () => {
    await fetch_tab(active_tab.value)
  }

  const preload_all_tabs = async () => {
    await fetch_tab(active_tab.value)
    for (const tab_key of tab_keys) {
      if (tab_key === active_tab.value) continue
      void fetch_tab(tab_key)
    }
  }

  const apply_search_and_reload = async (keyword: string) => {
    set_search_keyword(keyword)
    invalidate_all_tabs()
    await fetch_tab(active_tab.value, { force: true, page: 1 })
    for (const tab_key of tab_keys) {
      if (tab_key === active_tab.value) continue
      void fetch_tab(tab_key, { force: true, page: 1 })
    }
  }

  const refresh_after_mutation = async () => {
    invalidate_all_tabs()
    await fetch_tab(active_tab.value, { force: true, page: 1 })
    for (const tab_key of tab_keys) {
      if (tab_key === active_tab.value) continue
      void fetch_tab(tab_key, { force: true, page: 1 })
    }
  }

  const reset_store = () => {
    abort_all_requests()
    active_tab.value = '0'
    search_keyword.value = ''
    for (const tab_key of tab_keys) {
      Object.assign(tabs[tab_key], create_tab_state())
      request_seq[tab_key] = 0
    }
  }

  return {
    active_tab,
    search_keyword,
    page_size,
    tabs,
    active_state,
    abort_all_requests,
    invalidate_all_tabs,
    set_active_tab,
    set_search_keyword,
    set_active_page,
    fetch_tab,
    ensure_active_loaded,
    preload_all_tabs,
    apply_search_and_reload,
    refresh_after_mutation,
    reset_store
  }
})
