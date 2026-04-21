<template>
  <div class="w-full">
    <header class="mb-8 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight">Performans Raporları</h1>
        <p class="text-sm text-gray-400 mt-1">İnfocu performans dağılımları ve verilerin dışa aktarımı.</p>
      </div>
      <div>
         <!-- The actual ReportExport component handles date picking and downloading -->
         <ReportExport />
      </div>
    </header>

    <div class="w-full bg-dark-surface border border-dark-border rounded-xl shadow-xl overflow-hidden mt-8">
      <div class="p-6 border-b border-dark-border bg-dark-bg/30 flex justify-between items-center">
        <div>
          <h2 class="text-lg font-bold text-white">Bu Ayın Personel Performansları</h2>
          <p class="text-xs text-gray-400 mt-1">Sisteme kayıtlı infocuların hakediş ve satış tutarları.</p>
        </div>
        <!-- Refresh button -->
        <button @click="fetchPerformanceReport" class="p-2 text-ocean-400 hover:bg-ocean-900/30 rounded-lg transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
        </button>
      </div>
      
      <div class="overflow-x-auto w-full">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead class="text-xs text-gray-400 uppercase tracking-wider bg-dark-bg/80">
            <tr>
              <th class="py-4 px-6 font-semibold">İnfocu</th>
              <th class="py-4 px-6 font-semibold">Para Birimi</th>
              <th class="py-4 px-6 font-semibold text-right">Ham Satış</th>
              <th class="py-4 px-6 font-semibold text-right">Net Satış (Base)</th>
              <th class="py-4 px-6 font-semibold text-right text-neon-turquoise">Hakediş (Komisyon)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-dark-border">
            <tr v-if="isLoading">
              <td colspan="5" class="py-12 text-center text-ocean-500 animate-pulse">
                Rapor verileri hesaplanıyor...
              </td>
            </tr>
            <tr v-else-if="performanceData.length === 0">
              <td colspan="5" class="py-12 text-center text-gray-500">
                Bu tarih aralığında performans kaydı bulunamadı.
              </td>
            </tr>
            <tr v-for="(item, idx) in performanceData" :key="idx" class="hover:bg-ocean-900/10 transition-colors">
              <td class="py-4 px-6 text-white font-medium">{{ item.infocu }}</td>
              <td class="py-4 px-6 text-gray-400">{{ item.currency }}</td>
              <td class="py-4 px-6 text-right text-gray-300">{{ item.raw_sale }}</td>
              <td class="py-4 px-6 text-right text-ocean-300 font-bold">{{ item.base_sale }}</td>
              <td class="py-4 px-6 text-right text-neon-turquoise font-extrabold">{{ item.base_commission }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/axios'
import ReportExport from '@/components/Admin/ReportExport.vue'

const performanceData = ref([])
const isLoading = ref(true)

const getLocalISODate = (dateObj) => {
  const offset = dateObj.getTimezoneOffset()
  const localDate = new Date(dateObj.getTime() - (offset * 60 * 1000))
  return localDate.toISOString().split('T')[0]
}

const fetchPerformanceReport = async () => {
  try {
    isLoading.value = true
    const date = new Date()
    const firstDay = getLocalISODate(new Date(date.getFullYear(), date.getMonth(), 1))
    const today = getLocalISODate(date)
    
    const res = await api.get('/reports/performance', { 
      params: { start_date: firstDay, end_date: today } 
    })
    
    if (res.data && res.data.data) {
      performanceData.value = res.data.data
    }
  } catch (error) {
    console.error('Data fetch error:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchPerformanceReport()
})
</script>
