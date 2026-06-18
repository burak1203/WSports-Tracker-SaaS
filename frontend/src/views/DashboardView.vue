<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-slate-800">
        {{ authStore.user?.role === 'admin' ? 'Finansal Özet' : 'Kişisel Performansım' }}
      </h1>
      <button @click="fetchDashboardData" class="text-sm bg-white border border-gray-200 text-gray-600 px-3 py-1.5 rounded hover:bg-gray-50 transition-colors shadow-sm">
        ↻ Yenile
      </button>
    </div>

    <div v-if="isLoading" class="flex justify-center py-20 text-gray-400">
      <span class="animate-pulse">Veriler yükleniyor...</span>
    </div>

    <div v-else-if="authStore.user?.role === 'admin'" class="space-y-6">
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

    <div v-else-if="['infocu', 'yuzdeci'].includes(authStore.user?.role)" class="space-y-6">
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-2xl shadow-lg border border-slate-700 text-white">
          <p class="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-1">Toplam Hakediş (TRY Karşılığı)</p>
          <p class="text-4xl font-black">{{ formatCurrency(totalEarningsTRY) }}</p>
          <div class="mt-2 text-xs font-medium bg-white/10 inline-block px-2 py-1 rounded">Tüm kurların anlık TL toplamı</div>
        </div>

        <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col justify-center">
          <div class="flex justify-between items-end mb-2">
            <div>
              <p class="text-sm font-semibold text-gray-500 uppercase tracking-wider">Aylık Ciro Hedefi</p>
              <p class="text-lg font-bold text-slate-700">{{ formatCurrency(myTarget) }}</p>
            </div>
            <span class="text-2xl font-black" :class="targetProgress >= 100 ? 'text-green-500' : 'text-blue-600'">
              %{{ targetProgress.toFixed(1) }}
            </span>
          </div>
          
          <div class="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
            <div 
              class="h-3 rounded-full transition-all duration-1000 ease-out" 
              :class="targetProgress >= 100 ? 'bg-green-500' : 'bg-blue-600'"
              :style="{ width: targetProgress + '%' }">
            </div>
          </div>
          
          <div class="mt-2 flex justify-between items-center text-xs">
            <span class="font-bold text-slate-600">Yaptığım Ciro: {{ formatCurrency(myGeneratedRevenue) }}</span>
            <span v-if="targetProgress >= 100" class="text-green-600 font-bold flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
              Hedefe ulaşıldı!
            </span>
            <span v-else class="text-gray-400 font-medium">
              Kalan: {{ formatCurrency(myTarget - myGeneratedRevenue) }}
            </span>
          </div>
        </div>
      </div>

      <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
        <h3 class="font-bold text-slate-800 mb-6">Para Birimi Detayları</h3>
        
        <div v-if="!myEarnings || myEarnings.length === 0" class="text-sm text-gray-400 py-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-200">
          Bu tarih aralığında henüz bir hakedişiniz bulunmuyor.
        </div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="earning in myEarnings" :key="earning.currency" class="bg-slate-50 p-5 rounded-xl border border-slate-200 hover:border-blue-300 transition-colors">
            <span class="text-sm font-bold text-slate-500 block mb-1">{{ earning.currency }} Kasası</span>
            <span class="text-2xl font-black text-slate-800 block mb-2">{{ earning.total_commission }}</span>
            <span class="text-xs text-slate-400 font-medium pt-2 border-t border-slate-200 block">
              ~ {{ formatCurrency(earning.total_try_equivalent) }}
            </span>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/utils/axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const stats = ref({
  total_revenue: 0,
  total_expenses: 0,
  total_earnings: 0,
  net_profit: 0,
  daily_trend: [],
  activity_share: []
})
const myEarnings = ref([])
const myTarget = ref(0)
const myGeneratedRevenue = ref(0) // Yeni: Yaptığım Toplam Ciro
const isLoading = ref(true)

const totalEarningsTRY = computed(() => {
  if (!myEarnings.value || myEarnings.value.length === 0) return 0
  return myEarnings.value.reduce((acc, curr) => acc + Number(curr.total_try_equivalent || 0), 0)
})

const targetProgress = computed(() => {
  if (!myTarget.value || myTarget.value === 0) return 0
  const progress = (myGeneratedRevenue.value / myTarget.value) * 100
  return progress > 100 ? 100 : progress
})

const fetchDashboardData = async () => {
  isLoading.value = true
  try {
    const today = new Date()
    const year = today.getFullYear()
    const month = String(today.getMonth() + 1).padStart(2, '0')
    const day = String(today.getDate()).padStart(2, '0')
    
    const end_date = `${year}-${month}-${day}`
    const start_date = `${year}-${month}-01`
    
    if (authStore.user?.role === 'admin') {
      const response = await axios.get('/reports/dashboard', { params: { start_date, end_date } })
      stats.value = response.data
    } else if (['infocu', 'yuzdeci'].includes(authStore.user?.role)) {
      const response = await axios.get('/reports/me/earnings', { params: { start_date, end_date } })
      myEarnings.value = response.data.data
      myTarget.value = response.data.target_revenue
      myGeneratedRevenue.value = response.data.generated_revenue
    }
  } catch (error) {
    console.error("Veri çekilirken hata oluştu:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})

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

</script>