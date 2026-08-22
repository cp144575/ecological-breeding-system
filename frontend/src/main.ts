import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import './style.css'
import './styles/theme.css' // Import new theme

if (import.meta.env.DEV) {
  const original_warn = console.warn.bind(console)
  console.warn = (...args: any[]) => {
    if (args.length === 1 && args[0] && typeof args[0] === 'object' && args[0].name === 'ElementPlusError') {
      const element_plus_error = args[0] as any
      original_warn(element_plus_error?.message || element_plus_error)
      return
    }
    original_warn(...args)
  }
}

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app')
