<template>
  <div class="w-full">
    <header class="mb-8 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight">Satış Paneli</h1>
        <p class="text-sm text-gray-400 mt-1">Sisteme düşen tüm satışları görüntüleyin ve yeni satış ekleyin.</p>
      </div>
      <!-- Optional Date or Action Buttons can go here -->
    </header>

    <div class="flex flex-col gap-8 w-full">
      
      <!-- Quick Sale Form (Only for Infocu, or maybe Admin too? Contract doesn't prevent Admin) -->
      <div v-if="canAddSale" class="w-full bg-dark-surface border border-dark-border rounded-xl shadow-xl p-6">
        <h2 class="text-lg font-bold text-white mb-6 border-b border-dark-border pb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-neon-turquoise" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
          Yeni Satış Ekle
        </h2>
        <QuickSale @sale-added="fetchSales" />
      </div>

      <!-- Sales List Table -->
      <div class="w-full bg-dark-surface border border-dark-border rounded-xl shadow-xl overflow-hidden">
        <div class="p-6 border-b border-dark-border bg-dark-bg/30">
          <h2 class="text-lg font-bold text-white">Bu Günün Kayıtları (Son Satışlar)</h2>
          <p class="text-xs text-gray-400 mt-1">Sisteme işlenmiş son 100 satış listelenmektedir.</p>
        </div>
        
        <div v-if="isLoadingSales" class="py-12 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-neon-turquoise"></div>
          <p class="mt-2 text-sm text-gray-400">Veriler yükleniyor...</p>
        </div>
        
        <div v-else-if="sales.length === 0" class="py-12 text-center text-gray-500">
          <svg class="w-12 h-12 mx-auto mb-3 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path></svg>
          Hiç satış kaydı bulunamadı.
        </div>
        
        <div v-else class="overflow-x-auto w-full">
          <table class="w-full text-left text-sm whitespace-nowrap">
            <thead class="text-xs text-gray-400 uppercase tracking-wider bg-dark-bg/80">
              <tr>
                <th class="py-4 px-6 font-semibold">Tarih</th>
                <th class="py-4 px-6 font-semibold">Statü</th>
                <th class="py-4 px-6 font-semibold">Personel</th>
                <th class="py-4 px-6 font-semibold">Aktivite</th>
                <th class="py-4 px-6 font-semibold text-right">Para Birimi</th>
                <th class="py-4 px-6 font-semibold text-right">Nakit</th>
                <th class="py-4 px-6 font-semibold text-right">Kredi Kartı</th>
                <th class="py-4 px-6 font-semibold text-right">İşlem</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-dark-border">
              <TransitionGroup name="list">
                <tr v-for="sale in sales" :key="sale.id" class="hover:bg-ocean-900/10 transition-colors">
                  <td class="py-4 px-6 text-gray-300">{{ formatDate(sale.created_at) }}</td>
                  <td class="py-4 px-6">
                    <span v-if="sale.status === 'pending'" class="px-2 py-1 bg-yellow-500/20 text-yellow-500 text-xs rounded-full border border-yellow-500/30">Bekliyor</span>
                    <span v-else-if="sale.status === 'approved'" class="px-2 py-1 bg-green-500/20 text-green-500 text-xs rounded-full border border-green-500/30">Onaylandı</span>
                    <span v-else class="px-2 py-1 bg-red-500/20 text-red-500 text-xs rounded-full border border-red-500/30">İptal</span>
                  </td>
                  <td class="py-4 px-6 text-white font-medium">{{ getUserName(sale.added_by_user_id) }}</td>
                  <td class="py-4 px-6 text-neon-turquoise">{{ getActivityName(sale.activity_id) }}</td>
                  <td class="py-4 px-6 text-right text-gray-400">{{ sale.currency }}</td>
                  <td class="py-4 px-6 text-right text-green-400 font-bold">{{ sale.cash_amount > 0 ? formatCurrency(sale.cash_amount) : '-' }}</td>
                  <td class="py-4 px-6 text-right text-ocean-400 font-bold">{{ sale.cc_amount > 0 ? formatCurrency(sale.cc_amount) : '-' }}</td>
                  <td class="py-4 px-6 text-right">
                    <button v-if="sale.status === 'pending' && canApprove" @click="approveSale(sale.id)" class="px-3 py-1 bg-neon-turquoise/10 text-neon-turquoise border border-neon-turquoise/30 rounded hover:bg-neon-turquoise hover:text-dark-bg transition-colors text-xs font-bold">
                      Onayla
                    </button>
                  </td>
                </tr>
              </TransitionGroup>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Earnings Table -->
    <div class="w-full bg-dark-surface border border-dark-border rounded-xl shadow-xl overflow-hidden mt-8">
      <div class="p-6 border-b border-dark-border bg-dark-bg/30">
        <h2 class="text-lg font-bold text-white text-neon-turquoise">Hakedişler (Komisyonlar)</h2>
        <p class="text-xs text-gray-400 mt-1">Onaylanan satışlardan kazanılan tutarlar.</p>
      </div>
      
      <div v-if="isLoadingEarnings" class="py-8 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-neon-turquoise"></div>
      </div>
      <div v-else-if="earnings.length === 0" class="py-8 text-center text-gray-500">
        Henüz komisyon kaydınız bulunmuyor.
      </div>
      <div v-else class="overflow-x-auto w-full">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead class="text-xs text-gray-400 uppercase tracking-wider bg-dark-bg/80">
            <tr>
              <th class="py-4 px-6 font-semibold">Tarih</th>
              <th class="py-4 px-6 font-semibold" v-if="['admin', 'kasa'].includes(authStore.userRole)">Personel</th>
              <th class="py-4 px-6 font-semibold">Açıklama</th>
              <th class="py-4 px-6 font-semibold text-right">Para Birimi</th>
              <th class="py-4 px-6 font-semibold text-right">Tutar</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-dark-border">
            <tr v-for="earn in earnings" :key="earn.id" class="hover:bg-ocean-900/10 transition-colors">
              <td class="py-4 px-6 text-gray-300">{{ formatDate(earn.created_at) }}</td>
              <td class="py-4 px-6 text-white font-medium" v-if="['admin', 'kasa'].includes(authStore.userRole)">{{ getUserName(earn.user_id) }}</td>
              <td class="py-4 px-6 text-white">{{ earn.description }}</td>
              <td class="py-4 px-6 text-right text-gray-400">{{ earn.currency }}</td>
              <td class="py-4 px-6 text-right text-neon-turquoise font-extrabold">{{ formatCurrency(earn.calculated_amount) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/axios'
import { useToast } from 'vue-toastification'
import QuickSale from '@/components/QuickSale.vue'

const authStore = useAuthStore()
const toast = useToast()
const sales = ref([])
const earnings = ref([])
const usersMap = ref({})
const activitiesMap = ref({})
const isLoadingSales = ref(true)
const isLoadingEarnings = ref(false)

const canAddSale = computed(() => ['infocu', 'admin', 'kasa'].includes(authStore.userRole))
const canApprove = computed(() => ['admin', 'kasa'].includes(authStore.userRole))

const formatDate = (dateString) => {
  if (!dateString) return ''
  const d = new Date(dateString)
  return d.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount)
}

const getUserName = (id) => {
  return usersMap.value[id] || `#${id}`
}

const getActivityName = (id) => {
  return activitiesMap.value[id] || `#${id}`
}

const fetchData = async () => {
  try {
    isLoadingSales.value = true
    
    // Fetch mapping data
    const [usersRes, activitiesRes] = await Promise.all([
      api.get('/users/').catch(() => ({ data: [] })),
      api.get('/activities/').catch(() => ({ data: [] }))
    ])
    
    const uMap = {}
    if (usersRes.data) {
      usersRes.data.forEach(u => uMap[u.id] = u.full_name)
    }
    usersMap.value = uMap
    
    const aMap = {}
    if (activitiesRes.data) {
      activitiesRes.data.forEach(a => aMap[a.id] = a.name)
    }
    activitiesMap.value = aMap

    // Fetch sales
    fetchSales()
    
    // Fetch earnings for everyone
    isLoadingEarnings.value = true
    const earnRes = await api.get('/earnings/', { params: { limit: 100 } }).catch(() => ({ data: [] }))
    earnings.value = earnRes.data || []
    isLoadingEarnings.value = false
    
  } catch (error) {
    console.error('Initial data fetch error:', error)
  }
}

const fetchSales = async () => {
  try {
    isLoadingSales.value = true
    const res = await api.get('/sales/', { params: { limit: 100 } })
    sales.value = res.data || []
  } catch (error) {
    console.error('Data fetch error:', error)
  } finally {
    isLoadingSales.value = false
  }
}

const approveSale = async (id) => {
  try {
    await api.put(`/sales/${id}/approve`)
    toast.success('Satış onaylandı ve komisyonlar dağıtıldı!')
    fetchSales()
    // Refresh earnings table too
    const earnRes = await api.get('/earnings/', { params: { limit: 100 } }).catch(() => ({ data: [] }))
    earnings.value = earnRes.data || []
  } catch (error) {
    console.error('Approve error:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
