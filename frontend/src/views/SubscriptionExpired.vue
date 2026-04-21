<template>
  <div class="flex items-center justify-center min-h-screen bg-dark-bg p-4">
    <div class="card max-w-md w-full text-center border-red-900/50 shadow-red-900/20">
      <div class="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-white mb-2">Abonelik Süreniz Doldu</h1>
      <p class="text-gray-400 mb-8">Lisans süreniz sona ermiştir. Sistemi kullanmaya devam etmek için lütfen ödeme işlemini gerçekleştirin.</p>
      
      <button @click="logout" class="btn-primary w-full">Giriş Ekranına Dön</button>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
