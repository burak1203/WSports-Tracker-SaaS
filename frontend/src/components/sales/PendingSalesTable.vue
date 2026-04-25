<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col h-full">
    <div class="p-4 border-b border-gray-100 bg-slate-50 flex items-center justify-between">
      <h3 class="font-bold text-slate-800 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-orange-500 animate-pulse"></span>
        Onay Bekleyenler
      </h3>
      <button @click="fetchPendingSales" class="text-sm text-blue-600 font-semibold hover:text-blue-800">
        Yenile ↻
      </button>
    </div>

    <div class="p-4 flex-1 overflow-y-auto">
      <div v-if="isLoading" class="text-center text-sm text-gray-500 py-4">Yükleniyor...</div>
      
      <div v-else-if="pendingSales.length === 0" class="text-center text-sm text-gray-400 py-8">
        Bekleyen satış bulunmuyor.
      </div>

      <div v-else class="space-y-3">
        <div 
          v-for="sale in pendingSales" 
          :key="sale.id" 
          class="p-3 bg-white border border-orange-100 rounded-lg shadow-sm hover:shadow transition-shadow"
        >
          <div class="flex justify-between items-start mb-2">
            <div>
              <span class="text-xs font-bold bg-slate-100 text-slate-600 px-2 py-1 rounded">
                #{{ sale.id }} - {{ getActivityName(sale.activity_id) }}
              </span>
            </div>
            <span class="text-[10px] font-semibold uppercase tracking-wider text-orange-600 bg-orange-50 px-2 py-0.5 rounded">
              Beklemede
            </span>
          </div>

          <div class="text-sm font-medium text-slate-700 my-2">
            {{ formatAmounts(sale) }}
          </div>

          <div class="flex gap-2 mt-3 pt-3 border-t border-gray-50" v-if="authStore.user?.role === 'admin' || authStore.user?.role === 'kasa'">
            <button 
              @click="approveSale(sale.id)" 
              class="flex-1 bg-green-50 text-green-700 font-semibold text-xs py-2 rounded hover:bg-green-100 transition-colors"
            >
              ✓ Onayla
            </button>
            <button 
              @click="cancelSale(sale.id)" 
              class="flex-1 bg-red-50 text-red-700 font-semibold text-xs py-2 rounded hover:bg-red-100 transition-colors"
            >
              ✕ İptal
            </button>
          </div>
          <div v-else class="mt-3 pt-3 border-t border-gray-50 text-xs text-center text-gray-400">
            Onay yetkiniz yok
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCoreStore } from '@/stores/core'
import axios from '@/utils/axios'

const authStore = useAuthStore()
const coreStore = useCoreStore()
const pendingSales = ref([])
const isLoading = ref(false)

const fetchPendingSales = async () => {
  isLoading.value = true
  try {
    const res = await axios.get('/sales/')
    // Sadece pending olanları filtrele
    pendingSales.value = res.data.filter(s => s.status === 'pending')
  } catch (error) {
    console.error("Satışlar çekilemedi", error)
  } finally {
    isLoading.value = false
  }
}

const approveSale = async (id) => {
  try {
    await axios.put(`/sales/${id}/approve`)
    fetchPendingSales() // Tabloyu güncelle
  } catch (error) {
    alert("Onaylanırken hata oluştu!")
  }
}

const cancelSale = async (id) => {
  if(!confirm("Bu satışı iptal etmek istediğinize emin misiniz?")) return
  try {
    await axios.delete(`/sales/${id}`)
    fetchPendingSales()
  } catch (error) {
    alert("İptal edilirken hata oluştu!")
  }
}

// Yardımcı Fonksiyonlar
const getActivityName = (id) => {
  const act = coreStore.activities.find(a => a.id === id)
  return act ? act.name : 'Bilinmeyen Aktivite'
}

const formatAmounts = (sale) => {
  let parts = []
  if (sale.try_cash > 0) parts.push(`${parseFloat(sale.try_cash)}₺ Nakit`)
  if (sale.try_cc > 0) parts.push(`${parseFloat(sale.try_cc)}₺ KK`)
  if (sale.eur_cash > 0) parts.push(`${parseFloat(sale.eur_cash)}€ Nakit`)
  if (sale.eur_cc > 0) parts.push(`${parseFloat(sale.eur_cc)}€ KK`)
  if (sale.usd_cash > 0) parts.push(`${parseFloat(sale.usd_cash)}$ Nakit`)
  if (sale.usd_cc > 0) parts.push(`${parseFloat(sale.usd_cc)}$ KK`)
  if (sale.gbp_cash > 0) parts.push(`${parseFloat(sale.gbp_cash)}£ Nakit`)
  if (sale.gbp_cc > 0) parts.push(`${parseFloat(sale.gbp_cc)}£ KK`)
  return parts.join(' + ')
}

onMounted(() => {
  fetchPendingSales()
})
</script>