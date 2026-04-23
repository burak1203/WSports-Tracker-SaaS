<template>
  <div class="flex h-screen bg-gray-100">
    <aside class="w-64 bg-slate-900 text-white flex flex-col hidden md:flex">
      <div class="p-4 text-xl font-bold border-b border-slate-800">
        Wsports Tracker
      </div>
      <nav class="flex-1 p-4 space-y-2">
        <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-slate-400 hover:bg-slate-800 hover:text-white" active-class="bg-blue-600 shadow-lg shadow-blue-900/20 text-white !text-white">
          <span>📊</span> Dashboard
        </router-link>
        <router-link to="/sales" class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-slate-400 hover:bg-slate-800 hover:text-white" active-class="bg-blue-600 shadow-lg shadow-blue-900/20 text-white !text-white">
          <span>💰</span> Satış Paneli
        </router-link>
        <router-link v-if="authStore.user?.role === 'admin'" to="/system" class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-slate-400 hover:bg-slate-800 hover:text-white" active-class="bg-blue-600 shadow-lg shadow-blue-900/20 text-white !text-white">
          <span>⚙️</span> Sistem Yönetimi
        </router-link>
      </nav>
      <div class="p-4 border-t border-slate-800">
        <button @click="handleLogout" class="w-full text-left px-4 py-2 text-red-400 hover:bg-slate-800 rounded">
          Çıkış Yap
        </button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white shadow-sm flex items-center justify-between px-6 z-10">
        <div class="text-xl font-semibold text-gray-800">
          {{ $route.name }}
        </div>
        <div class="flex items-center gap-4">
          <span class="text-sm font-medium text-gray-600">
            Hoş geldin, {{ authStore.user?.full_name }}
          </span>
        </div>
      </header>

      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
        <div v-if="!coreStore.isLoaded" class="flex justify-center items-center h-full text-gray-500">
          Sistem verileri yükleniyor...
        </div>
        <router-view v-else></router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCoreStore } from '@/stores/core'

const router = useRouter()
const authStore = useAuthStore()
const coreStore = useCoreStore()

onMounted(async () => {
  if (authStore.token && !coreStore.isLoaded) {
    await coreStore.fetchInitialData()
  }
})

const handleLogout = () => {
  authStore.logout() // Bunu auth.js içinde yazmıştık
  router.push('/login')
}
</script>