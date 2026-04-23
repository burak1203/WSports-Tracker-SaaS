<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900 px-4">
    <div class="max-w-md w-full bg-white rounded-2xl shadow-2xl overflow-hidden">
      <div class="p-8">
        <div class="text-center mb-10">
          <h1 class="text-3xl font-extrabold text-slate-800">Wsports Tracker</h1>
          <p class="text-slate-500 mt-2">Sisteme erişmek için giriş yapın</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-sm font-bold text-slate-700 mb-2">Kullanıcı Adı</label>
            <input 
              v-model="username" 
              type="text" 
              required
              class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              placeholder="admin_yilmaz"
            >
          </div>

          <div>
            <label class="block text-sm font-bold text-slate-700 mb-2">Şifre</label>
            <input 
              v-model="password" 
              type="password" 
              required
              class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
              placeholder="••••••••"
            >
          </div>

          <button 
            type="submit" 
            :disabled="isLoading"
            class="w-full bg-blue-600 text-white font-bold py-4 rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-200 disabled:opacity-50"
          >
            {{ isLoading ? 'Giriş Yapılıyor...' : 'Giriş Yap' }}
          </button>
        </form>

        <div v-if="error" class="mt-6 p-4 bg-red-50 border border-red-100 text-red-600 rounded-xl text-sm text-center font-medium">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from '@/utils/axios'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  isLoading.value = true
  
  try {
    // Backend OAuth2 Form Data beklediği için veriyi URLSearchParams ile sarıyoruz
    const params = new URLSearchParams()
    params.append('username', username.value)
    params.append('password', password.value)

    const response = await axios.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    // Gelen token ve kullanıcı bilgilerini Pinia'ya ve localStorage'a mühürle
    authStore.setAuth(response.data.access_token, response.data.user)
    
    // Başarılı girişten sonra ana sayfaya (Dashboard) uçur
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Giriş başarısız. Bilgileri kontrol edin.'
  } finally {
    isLoading.value = false
  }
}
</script>