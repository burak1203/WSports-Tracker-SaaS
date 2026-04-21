<template>
  <div class="min-h-screen bg-dark-bg p-4 md:p-8 pb-20">
    <header class="mb-8 flex justify-between items-center bg-dark-surface p-4 rounded-xl border border-dark-border shadow-lg">
      <div>
        <h1 class="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-ocean-500 to-neon-turquoise">İnfocu Paneli</h1>
        <p class="text-sm text-gray-400 mt-1">Hoş Geldin, <span class="text-white">{{ authStore.user?.full_name || 'Kullanıcı' }}</span></p>
      </div>
      <button @click="logout" class="btn-primary text-sm bg-red-900/50 hover:bg-red-800 text-red-100 border border-red-800 shadow-none">Çıkış</button>
    </header>
    
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- Left Column -->
      <div class="lg:col-span-8 space-y-6">
        
        <!-- Progress Bar Card -->
        <div class="card relative">
          <h2 class="text-lg font-semibold mb-4 text-white flex justify-between items-center">
            <span>Günlük Hedef & Hakediş</span>
            <span class="text-neon-turquoise text-sm bg-neon-turquoise/10 px-3 py-1 rounded-full border border-neon-turquoise/20">Bugün</span>
          </h2>
          
          <div class="mb-6">
             <div class="flex justify-between text-sm mb-2">
                <span class="text-gray-400">Hedef Ciro (Tahmini)</span>
                <span class="font-bold text-white">{{ currentSales }}€ / <span class="text-gray-500">{{ targetCiro }}€</span></span>
             </div>
             <!-- Animated Progress Bar -->
             <div class="w-full bg-dark-bg rounded-full h-5 overflow-hidden border border-dark-border relative">
               <div class="absolute inset-0 bg-gradient-to-r from-ocean-800 to-ocean-600 opacity-50"></div>
               <div 
                 class="h-full rounded-full transition-all duration-1000 ease-out relative overflow-hidden" 
                 :class="progressPercentage >= 100 ? 'bg-gradient-to-r from-green-500 to-neon-turquoise' : 'bg-gradient-to-r from-ocean-500 to-neon-turquoise'"
                 :style="{ width: `${progressPercentage}%` }"
               >
                 <div class="absolute inset-0 w-full h-full bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPgo8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI4IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMSI+PC9yZWN0Pgo8L3N2Zz4=')] opacity-20"></div>
               </div>
             </div>
          </div>
          
          <div class="flex justify-between items-center pt-4 border-t border-dark-border">
            <span class="text-gray-400">Tahmini Hakedişiniz</span>
            <span class="text-2xl font-bold text-neon-turquoise">€{{ estimatedCommission }}</span>
          </div>
        </div>

        <!-- Recent Sales Log -->
        <div class="card">
          <h2 class="text-lg font-semibold mb-4 text-white">Son Satışlarım</h2>
          
          <div v-if="isLoadingSales" class="py-8 text-center text-ocean-500 animate-pulse">
            Satışlar yükleniyor...
          </div>
          <div v-else-if="recentSales.length === 0" class="py-8 text-center text-gray-500">
            Henüz satış bulunmuyor.
          </div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead class="text-gray-400 border-b border-dark-border">
                <tr>
                  <th class="pb-3 font-medium">Saat</th>
                  <th class="pb-3 font-medium">Aktivite</th>
                  <th class="pb-3 font-medium text-right">Nakit</th>
                  <th class="pb-3 font-medium text-right">Kredi Kartı</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-dark-border">
                <tr v-for="sale in recentSales" :key="sale.id" class="hover:bg-dark-bg/50 transition-colors">
                  <td class="py-3 text-gray-300">{{ formatTime(sale.created_at) }}</td>
                  <td class="py-3 text-white">Aktivite #{{ sale.activity_id }}</td>
                  <td class="py-3 text-right text-green-400">{{ sale.cash_amount > 0 ? sale.cash_amount : '-' }}</td>
                  <td class="py-3 text-right text-ocean-400">{{ sale.cc_amount > 0 ? sale.cc_amount : '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="lg:col-span-4">
        <QuickSale @sale-added="fetchDashboardData" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/utils/axios'
import QuickSale from '@/components/QuickSale.vue'

const authStore = useAuthStore()
const router = useRouter()

const targetCiro = ref(1000) // Mock target since it's not in UserResponse
const currentSales = ref(0)
const estimatedCommission = ref(0)
const recentSales = ref([])
const isLoadingSales = ref(true)

const progressPercentage = computed(() => {
  const pct = (currentSales.value / targetCiro.value) * 100
  return Math.min(pct, 100).toFixed(1)
})

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const d = new Date(dateString)
  return d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
}

const fetchDashboardData = async () => {
  isLoadingSales.value = true
  try {
    // 1. Fetch Sales Log
    const salesRes = await api.get('/sales/', { params: { limit: 10 } })
    // Assuming backend returns an array for successful get
    recentSales.value = salesRes.data || []
    
    // Calculate mock current sales from the recent list for demo purposes
    // In a real scenario, we'd use /api/reports/performance
    let total = 0
    recentSales.value.forEach(s => {
      total += parseFloat(s.cash_amount || 0) + parseFloat(s.cc_amount || 0)
    })
    
    // Simulate updating progress bar with a slight delay for smooth animation
    setTimeout(() => {
      currentSales.value = total
      estimatedCommission.value = (total * 0.1).toFixed(2) // Mock 10% commission
    }, 300)

  } catch (error) {
    console.error('Failed to fetch dashboard data', error)
  } finally {
    isLoadingSales.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>
