import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import { useToast } from 'vue-toastification'

const toast = useToast()

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request Interceptor
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response Interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response) {
      const status = error.response.status
      const authStore = useAuthStore()

      if (status === 401) {
        authStore.logout()
        router.push({ name: 'Login' })
        toast.error('Oturumunuz süresi doldu. Lütfen tekrar giriş yapın.')
      } else if (status === 402) {
        router.push({ name: 'SubscriptionExpired' })
        toast.warning('Abonelik süreniz doldu.')
      } else if (status === 422) {
        toast.error('Girdiğiniz bilgiler geçersiz. Lütfen kontrol edin.')
      } else if (status >= 500) {
        toast.error('Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.')
      }
    } else if (error.request) {
      toast.error('Sunucuya ulaşılamıyor. İnternet bağlantınızı kontrol edin.')
    }
    
    return Promise.reject(error)
  }
)

export default api
