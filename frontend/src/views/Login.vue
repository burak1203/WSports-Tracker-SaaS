<template>
  <div class="flex items-center justify-center min-h-screen bg-dark-bg p-4">
    <div class="card w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-neon-turquoise to-ocean-500">WSports Tracker</h1>
        <p class="text-gray-400 mt-2">Giriş Yapın</p>
      </div>
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Kullanıcı Adı</label>
          <input v-model="username" type="text" required class="w-full" placeholder="Kullanıcı adınızı girin" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Şifre</label>
          <input v-model="password" type="password" required class="w-full" placeholder="••••••••" />
        </div>
        <button type="submit" class="btn-neon w-full flex justify-center items-center h-12 text-lg" :disabled="isLoading">
          <span v-if="!isLoading">Giriş Yap</span>
          <span v-else class="animate-pulse">Giriş Yapılıyor...</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import api from '@/utils/axios'

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const handleLogin = async () => {
  isLoading.value = true
  try {
    const formData = new URLSearchParams()
    formData.append('username', username.value)
    formData.append('password', password.value)

    // Using form-urlencoded as specified in api-contract.json
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    const token = response.data.access_token
    
    const decodeJWT = (token) => {
      try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
      } catch(e) {
        return null;
      }
    }

    const payload = decodeJWT(token)
    const user = { id: payload.sub, role: payload.role, full_name: username.value }
    
    authStore.setAuth(token, user)
    toast.success('Giriş başarılı! Yönlendiriliyorsunuz...')
    
    // Yönlendirme Düzeltmesi: İnfocu admin paneline giremez
    if (user.role === 'infocu') {
      router.push({ name: 'SalesPanel' })
    } else {
      router.push({ name: 'Dashboard' })
    }
  } catch (error) {
    // Error is handled by interceptor, but we can catch specific ones here
    if(error.response?.status === 401) {
       toast.error('Hatalı kullanıcı adı veya şifre.')
    }
  } finally {
    isLoading.value = false
  }
}
</script>
