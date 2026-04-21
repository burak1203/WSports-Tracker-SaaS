<template>
  <div class="w-full">
    <header class="mb-8 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight">Dashboard</h1>
        <p class="text-sm text-gray-400 mt-1">Aylık finansal özetiniz ve performans göstergeleriniz.</p>
      </div>
      <div class="bg-dark-surface border border-dark-border rounded-lg p-2 flex gap-4 shadow-lg items-center">
        <div>
          <label class="block text-xs text-gray-400 mb-1">Başlangıç</label>
          <input v-model="startDate" @change="fetchMonthlyReport" type="date" class="w-full text-sm bg-dark-bg border border-dark-border rounded px-2 py-1 text-white focus:outline-none focus:border-neon-turquoise" />
        </div>
        <div>
          <label class="block text-xs text-gray-400 mb-1">Bitiş</label>
          <input v-model="endDate" @change="fetchMonthlyReport" type="date" class="w-full text-sm bg-dark-bg border border-dark-border rounded px-2 py-1 text-white focus:outline-none focus:border-neon-turquoise" />
        </div>
      </div>
    </header>

    <!-- Top 4 Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
      
      <!-- Total Revenue Card -->
      <div class="bg-dark-surface border border-dark-border rounded-xl shadow-xl p-6 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
           <svg class="w-16 h-16 text-neon-turquoise" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-neon-turquoise"></span> TOPLAM GELİR
        </h3>
        <div v-if="isDashboardLoading" class="h-10 animate-pulse bg-dark-bg rounded mt-2"></div>
        <div v-else class="relative z-10 mt-2">
          <span class="text-3xl font-extrabold text-white">{{ formatCurrency(dashboardData.total_revenue, 'TRY') }}</span>
        </div>
      </div>

      <!-- Base Expenses Card -->
      <div class="bg-dark-surface border border-dark-border rounded-xl shadow-xl p-6 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
           <svg class="w-16 h-16 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path></svg>
        </div>
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-red-500"></span> TOPLAM GİDER
        </h3>
        <div v-if="isDashboardLoading" class="h-10 animate-pulse bg-dark-bg rounded mt-2"></div>
        <div v-else class="relative z-10 mt-2">
           <span class="text-3xl font-bold text-red-400">{{ formatCurrency(dashboardData.total_expenses, 'TRY') }}</span>
        </div>
      </div>

      <!-- Total Earnings Card -->
      <div class="bg-dark-surface border border-dark-border rounded-xl shadow-xl p-6 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
           <svg class="w-16 h-16 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
        </div>
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-yellow-500"></span> HAKEDİŞLER
        </h3>
        <div v-if="isDashboardLoading" class="h-10 animate-pulse bg-dark-bg rounded mt-2"></div>
        <div v-else class="relative z-10 mt-2">
           <span class="text-3xl font-bold text-yellow-400">{{ formatCurrency(dashboardData.total_earnings, 'TRY') }}</span>
        </div>
      </div>

      <!-- Net Profit Card -->
      <div class="bg-dark-surface border border-dark-border rounded-xl shadow-xl p-6 relative overflow-hidden group">
        <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
           <svg class="w-16 h-16 text-ocean-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-ocean-400"></span> NET KÂR
        </h3>
        <div v-if="isDashboardLoading" class="h-10 animate-pulse bg-dark-bg rounded mt-2"></div>
        <div v-else class="relative z-10 mt-2">
           <span class="text-3xl font-bold text-ocean-300">{{ formatCurrency(dashboardData.net_profit, 'TRY') }}</span>
        </div>
      </div>

    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      
      <!-- Line Chart: Günlük Gelir Trendi -->
      <div class="bg-dark-surface border border-dark-border rounded-xl shadow-xl p-6">
        <h3 class="text-lg font-bold text-white mb-6 border-b border-dark-border pb-2">Günlük Gelir Trendi</h3>
        <div v-if="isDashboardLoading" class="h-[300px] flex justify-center items-center">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-neon-turquoise"></div>
        </div>
        <div v-else-if="dashboardData.daily_trend.length === 0" class="h-[300px] flex justify-center items-center text-gray-500">
          Bu ay henüz satış yapılmadı.
        </div>
        <apexchart v-else type="area" height="300" :options="lineChartOptions" :series="lineChartSeries"></apexchart>
      </div>

      <!-- Pie Chart: Aktivite Bazlı Gelir -->
      <div class="bg-dark-surface border border-dark-border rounded-xl shadow-xl p-6">
        <h3 class="text-lg font-bold text-white mb-6 border-b border-dark-border pb-2">Aktivite Bazlı Gelir</h3>
        <div v-if="isDashboardLoading" class="h-[300px] flex justify-center items-center">
          <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-neon-turquoise"></div>
        </div>
        <div v-else-if="dashboardData.activity_share.length === 0" class="h-[300px] flex justify-center items-center text-gray-500">
          Veri yok.
        </div>
        <apexchart v-else type="donut" height="300" :options="pieChartOptions" :series="pieChartSeries"></apexchart>
      </div>

    </div>

    <!-- Monthly Summary Table for extra detail -->
    <div class="w-full bg-dark-surface border border-dark-border rounded-xl shadow-xl overflow-hidden">
      <div class="p-6 border-b border-dark-border bg-dark-bg/30">
        <h2 class="text-lg font-bold text-white">Bu Ayın Döviz Kırılımı</h2>
      </div>
      <div class="overflow-x-auto w-full">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead class="text-xs text-gray-400 uppercase tracking-wider bg-dark-bg/80">
            <tr>
              <th class="py-4 px-6 font-semibold">Para Birimi</th>
              <th class="py-4 px-6 font-semibold text-right">Nakit</th>
              <th class="py-4 px-6 font-semibold text-right">Kredi Kartı</th>
              <th class="py-4 px-6 font-semibold text-right">Toplam Gelir (Base)</th>
              <th class="py-4 px-6 font-semibold text-right text-red-400">Toplam Gider</th>
              <th class="py-4 px-6 font-semibold text-right text-yellow-500">Ödenen Komisyon</th>
              <th class="py-4 px-6 font-semibold text-right text-ocean-300">Net Kâr</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-dark-border">
            <tr v-if="isLoading">
              <td colspan="7" class="py-8 text-center text-ocean-500 animate-pulse">Yükleniyor...</td>
            </tr>
            <tr v-else-if="monthlyData.length === 0">
              <td colspan="7" class="py-8 text-center text-gray-500">Kayıt bulunamadı.</td>
            </tr>
            <tr v-for="item in monthlyData" :key="item.currency" class="hover:bg-ocean-900/10 transition-colors">
              <td class="py-4 px-6 text-white font-bold">{{ item.currency }}</td>
              <td class="py-4 px-6 text-right text-green-400">{{ formatCurrency(item.raw_cash, item.currency) }}</td>
              <td class="py-4 px-6 text-right text-ocean-400">{{ formatCurrency(item.raw_cc, item.currency) }}</td>
              <td class="py-4 px-6 text-right text-neon-turquoise font-extrabold">{{ formatCurrency(item.base_revenue, item.currency) }}</td>
              <td class="py-4 px-6 text-right text-red-400 font-bold">{{ formatCurrency(item.base_expenses, item.currency) }}</td>
              <td class="py-4 px-6 text-right text-yellow-500 font-bold">{{ formatCurrency(item.base_earnings, item.currency) }}</td>
              <td class="py-4 px-6 text-right text-ocean-300 font-extrabold">{{ formatCurrency(item.net_profit, item.currency) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/axios'

// --- Table Data ---
const getLocalISODate = (dateObj) => {
  const offset = dateObj.getTimezoneOffset()
  const localDate = new Date(dateObj.getTime() - (offset * 60 * 1000))
  return localDate.toISOString().split('T')[0]
}

const todayDate = new Date()
const firstDayDate = new Date(todayDate.getFullYear(), todayDate.getMonth(), 1)

const startDate = ref(getLocalISODate(firstDayDate))
const endDate = ref(getLocalISODate(todayDate))

const monthlyData = ref([])
const isLoading = ref(true)

// --- Dashboard Aggregated Data & Charts ---
const dashboardData = ref({
  total_revenue: 0,
  total_expenses: 0,
  total_earnings: 0,
  net_profit: 0,
  daily_trend: [],
  activity_share: []
})
const isDashboardLoading = ref(true)

const formatCurrency = (amount, currency = 'TRY') => {
  return new Intl.NumberFormat('tr-TR', { 
    style: 'currency', 
    currency: currency,
    minimumFractionDigits: 2
  }).format(amount || 0)
}

// Line Chart Computed
const lineChartOptions = computed(() => ({
  chart: {
    type: 'area',
    foreColor: '#9ca3af',
    toolbar: { show: false },
    background: 'transparent'
  },
  theme: { mode: 'dark' },
  stroke: { curve: 'smooth', width: 3 },
  colors: ['#00e5ff'],
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.7,
      opacityTo: 0.1,
      stops: [0, 90, 100]
    }
  },
  xaxis: {
    categories: dashboardData.value.daily_trend.map(d => d.date),
    tooltip: { enabled: false }
  },
  yaxis: {
    labels: {
      formatter: (val) => new Intl.NumberFormat('tr-TR', { notation: 'compact' }).format(val)
    }
  },
  dataLabels: {
    enabled: false
  },
  tooltip: {
    theme: 'dark',
    y: {
      formatter: (val) => formatCurrency(val, 'TRY')
    }
  }
}))

const lineChartSeries = computed(() => [{
  name: 'Günlük Ciro',
  data: dashboardData.value.daily_trend.map(d => parseFloat(d.revenue))
}])

// Pie Chart Computed
const pieChartOptions = computed(() => ({
  chart: {
    type: 'donut',
    foreColor: '#9ca3af',
    background: 'transparent'
  },
  theme: { mode: 'dark' },
  labels: dashboardData.value.activity_share.map(d => d.activity_name),
  colors: ['#00e5ff', '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'],
  stroke: { show: false },
  plotOptions: {
    pie: {
      donut: {
        size: '70%'
      }
    }
  },
  dataLabels: {
    enabled: false
  },
  tooltip: {
    theme: 'dark',
    y: {
      formatter: (val) => formatCurrency(val, 'TRY')
    }
  }
}))

const pieChartSeries = computed(() => {
  return dashboardData.value.activity_share.map(d => parseFloat(d.revenue))
})


const fetchDashboardData = async (startStr, endStr) => {
  try {
    isDashboardLoading.value = true
    const res = await api.get('/reports/dashboard', {
      params: { start_date: startStr, end_date: endStr }
    })
    if (res.data) {
      dashboardData.value = res.data
    }
  } catch (error) {
    console.error('Dashboard data fetch error:', error)
  } finally {
    isDashboardLoading.value = false
  }
}

const fetchMonthlyReport = async () => {
  if (!startDate.value || !endDate.value) return

  try {
    isLoading.value = true
    
    fetchDashboardData(startDate.value, endDate.value)

    const res = await api.get('/reports/monthly', { 
      params: { start_date: startDate.value, end_date: endDate.value } 
    })
    
    if (res.data && res.data.data) {
      monthlyData.value = res.data.data
    }
  } catch (error) {
    console.error('Monthly table fetch error:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchMonthlyReport()
})
</script>
