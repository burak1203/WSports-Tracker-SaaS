<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-slate-800">Finansal Özet</h1>
      <button @click="fetchDashboardData" class="text-sm bg-white border border-gray-200 text-gray-600 px-3 py-1.5 rounded hover:bg-gray-50 transition-colors shadow-sm">
        ↻ Yenile
      </button>
    </div>

    <div v-if="isLoading" class="flex justify-center py-20 text-gray-400">
      <span class="animate-pulse">Veriler hesaplanıyor...</span>
    </div>

    <div v-else class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">Brüt Ciro</p>
          <p class="text-3xl font-black text-slate-800">{{ formatCurrency(stats.total_revenue) }}</p>
          <div class="mt-2 text-xs text-green-600 font-medium bg-green-50 inline-block px-2 py-1 rounded">Tüm onaylı satışlar</div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">Ödenen Hakedişler</p>
          <p class="text-3xl font-black text-orange-500">{{ formatCurrency(stats.total_earnings) }}</p>
          <div class="mt-2 text-xs text-orange-600 font-medium bg-orange-50 inline-block px-2 py-1 rounded">İnfocu/Yüzdelikçi payları</div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-1">Masraflar</p>
          <p class="text-3xl font-black text-red-500">{{ formatCurrency(stats.total_expenses) }}</p>
          <div class="mt-2 text-xs text-red-600 font-medium bg-red-50 inline-block px-2 py-1 rounded">Kasadan çıkanlar</div>
        </div>

        <div class="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-2xl shadow-lg border border-blue-700 text-white relative overflow-hidden">
          <div class="relative z-10">
            <p class="text-sm font-semibold text-blue-100 uppercase tracking-wider mb-1">Sistem Net Kârı</p>
            <p class="text-3xl font-black">{{ formatCurrency(stats.net_profit) }}</p>
            <div class="mt-2 text-xs text-white font-medium bg-white/20 inline-block px-2 py-1 rounded backdrop-blur-sm">Şirkette kalan net para</div>
          </div>
          <div class="absolute -right-6 -bottom-6 opacity-10">
            <svg class="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h3 class="font-bold text-slate-800 mb-6">Aktivite Bazlı Gelir Dağılımı</h3>
        
        <div v-if="stats.activity_share?.length === 0" class="text-sm text-gray-400 py-4 text-center">
          Henüz yeterli veri yok.
        </div>

        <div v-else class="space-y-5">
          <div v-for="(item, index) in stats.activity_share" :key="index" class="relative">
            <div class="flex justify-between items-end mb-1">
              <span class="text-sm font-bold text-slate-700">{{ item.activity_name }}</span>
              <span class="text-sm font-semibold text-slate-500">{{ formatCurrency(item.revenue) }}</span>
            </div>
            <div class="w-full bg-slate-100 rounded-full h-2.5">
              <div class="bg-blue-600 h-2.5 rounded-full" :style="{ width: calculatePercentage(item.revenue) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from '@/utils/axios'

const stats = ref({
  total_revenue: 0,
  total_expenses: 0,
  total_earnings: 0,
  net_profit: 0,
  daily_trend: [],
  activity_share: []
})

const isLoading = ref(true)

const fetchDashboardData = async () => {
  isLoading.value = true
  try {
    // Bugünün tarihini ve bu ayın ilk gününü YYYY-MM-DD formatında alıyoruz
    const today = new Date()
    const end_date = today.toISOString().split('T')[0]
    const start_date = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().split('T')[0]

    // Parametreleri backend'e gönderiyoruz
    const response = await axios.get('/reports/dashboard', {
      params: {
        start_date: start_date,
        end_date: end_date
      }
    })
    
    stats.value = response.data
  } catch (error) {
    console.error("Dashboard verisi çekilirken hata oluştu:", error)
  } finally {
    isLoading.value = false
  }
}

// Tüm cirolar içindeki yüzdesini hesapla (Bar genişliği için)
const calculatePercentage = (amount) => {
  if (stats.value.total_revenue <= 0) return 0
  const maxShare = Math.max(...stats.value.activity_share.map(a => parseFloat(a.revenue)))
  return (parseFloat(amount) / maxShare) * 100 // En çok satan aktiviteyi %100 genişlikte gösterir
}

const formatCurrency = (value) => {
  if (value === null || value === undefined) return '0.00₺'
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(value)
}

onMounted(() => {
  fetchDashboardData()
})
</script>