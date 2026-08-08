import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import i18n from './locales'
import { setupTiny } from './plugins/opentiny'
import { useUserStore } from './stores/user'
import { initTheme } from './utils/theme'
import './style.css'

initTheme()

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(i18n)
setupTiny(app)

const userStore = useUserStore()
if (userStore.token) {
  if (!userStore.isLogin) {
    userStore.clearSession()
  } else {
    userStore.scheduleExpireRedirect()
  }
}

app.mount('#app')
