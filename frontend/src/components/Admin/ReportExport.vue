<template>
  <div class="card bg-gradient-to-br from-dark-surface to-ocean-900/40 border border-dark-border">
    <h3 class="text-lg font-semibold mb-4 text-white border-b border-dark-border pb-2">Rapor Export</h3>
    
    <div class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-gray-400 mb-1">Başlangıç</label>
          <input v-model="startDate" type="date" class="w-full text-sm" />
        </div>
        <div>
          <label class="block text-xs text-gray-400 mb-1">Bitiş</label>
          <input v-model="endDate" type="date" class="w-full text-sm" />
        </div>
      </div>

      <div class="flex flex-col gap-2 pt-2">
        <button @click="downloadReport('monthly')" :disabled="isDownloading || !isValidDates" class="w-full px-4 py-2 bg-ocean-800 hover:bg-ocean-700 text-white text-sm rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          Aylık Rapor İndir
        </button>
        <button @click="downloadReport('performance')" :disabled="isDownloading || !isValidDates" class="w-full px-4 py-2 border border-ocean-600 text-ocean-400 hover:bg-ocean-900 text-sm rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Performans Raporu İndir
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/utils/axios'
import { useToast } from 'vue-toastification'

const toast = useToast()
const getLocalISODate = (dateObj) => {
  const offset = dateObj.getTimezoneOffset()
  const localDate = new Date(dateObj.getTime() - (offset * 60 * 1000))
  return localDate.toISOString().split('T')[0]
}

const todayDate = new Date()
const firstDayDate = new Date(todayDate.getFullYear(), todayDate.getMonth(), 1)

const startDate = ref(getLocalISODate(firstDayDate))
const endDate = ref(getLocalISODate(todayDate))
const isDownloading = ref(false)

const isValidDates = computed(() => {
  return startDate.value && endDate.value && startDate.value <= endDate.value
})

const downloadReport = async (type) => {
  if (!isValidDates.value) return
  
  isDownloading.value = true
  try {
    const url = type === 'monthly' ? '/reports/monthly/export' : '/reports/performance/export'
    
    const response = await api.get(url, {
      params: {
        start_date: startDate.value,
        end_date: endDate.value
      },
      responseType: 'blob' // Important for handling files
    })

    // Create a download link for the blob
    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = downloadUrl
    
    // Attempt to extract filename from header or use default
    const contentDisposition = response.headers['content-disposition']
    let fileName = `${type}_report_${startDate.value}_${endDate.value}.xlsx`
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/)
      if (match && match.length > 1) {
        fileName = match[1]
      }
    }
    
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    toast.success('Rapor başarıyla indirildi.')
  } catch (error) {
    console.error(error)
    toast.error('Rapor indirilirken bir hata oluştu.')
  } finally {
    isDownloading.value = false
  }
}
</script>
