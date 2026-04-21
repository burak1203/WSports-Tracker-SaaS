<template>
  <div class="min-h-screen flex bg-dark-bg">
    
    <!-- Mobile Header & Hamburger -->
    <header class="md:hidden fixed top-0 left-0 right-0 z-40 bg-dark-surface border-b border-dark-border px-4 py-3 flex justify-between items-center">
      <h2 class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-neon-turquoise to-ocean-500">WSports Admin</h2>
      <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="text-gray-300 hover:text-white">
        <svg v-if="!isMobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </header>

    <!-- Mobile Navigation Drawer -->
    <div v-if="isMobileMenuOpen" class="md:hidden fixed inset-0 z-30 bg-black/80 backdrop-blur-sm" @click="isMobileMenuOpen = false"></div>
    <aside :class="['fixed md:static inset-y-0 left-0 z-40 w-64 bg-dark-surface border-r border-dark-border transform transition-transform duration-300 ease-in-out md:translate-x-0 flex flex-col', isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full']">
      <div class="p-6 hidden md:block">
        <h2 class="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-neon-turquoise to-ocean-500">WSports Admin</h2>
        <p class="text-xs text-gray-500 mt-1 uppercase tracking-wider">{{ authStore.user?.role || 'Yetkili' }} Paneli</p>
      </div>
      <div class="p-6 md:hidden mt-12 border-b border-dark-border">
        <p class="text-xs text-gray-400 uppercase tracking-wider">Kullanıcı: <span class="text-white">{{ authStore.user?.full_name }}</span></p>
        <p class="text-xs text-neon-turquoise uppercase tracking-wider mt-1">Rol: {{ authStore.user?.role }}</p>
      </div>
      
      <nav class="flex-1 px-4 py-4 space-y-2 overflow-y-auto">
        <a href="#" class="block px-4 py-3 rounded-lg bg-ocean-900/50 text-neon-turquoise border border-ocean-800 transition-colors">Dashboard</a>
        
        <!-- Action Buttons (Only for Admin) -->
        <div v-if="authStore.userRole === 'admin'" class="pt-4 pb-2">
          <p class="text-xs font-semibold text-gray-500 uppercase tracking-wider px-2 mb-2">Hızlı İşlemler</p>
          <button @click="openUserModal" class="w-full text-left px-4 py-2 rounded-lg text-gray-300 hover:bg-ocean-900/30 hover:text-white transition-colors flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
            Personel Ekle
          </button>
          <button @click="openActivityModal" class="w-full text-left px-4 py-2 rounded-lg text-gray-300 hover:bg-ocean-900/30 hover:text-white transition-colors flex items-center gap-2 mt-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            Aktivite Ekle
          </button>
        </div>
      </nav>
      
      <div class="p-4 border-t border-dark-border">
        <button @click="logout" class="w-full text-left px-4 py-2 text-gray-400 hover:text-white flex items-center gap-2 transition-colors">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
          Çıkış Yap
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 p-4 pt-20 md:p-8 md:pt-8 overflow-y-auto w-full">
      <header class="hidden md:block mb-8">
        <h1 class="text-3xl font-bold text-white">Genel Bakış</h1>
        <p class="text-gray-400 mt-1">Sistemin anlık durumu ve son gerçekleşen satışlar.</p>
      </header>
      
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6 mb-8">
         <!-- Left Column (Widgets) -->
         <div class="md:col-span-8 grid grid-cols-1 sm:grid-cols-2 gap-6">
           <div class="card hover:shadow-neon-turquoise/10 hover:border-ocean-700">
              <h3 class="text-gray-400 text-sm flex items-center gap-2">
                <svg class="w-4 h-4 text-ocean-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                Tahmini Aylık Ciro
              </h3>
              <div v-if="isLoadingReports" class="h-10 mt-2 bg-dark-bg animate-pulse rounded"></div>
              <p v-else class="text-3xl font-bold text-white mt-2">{{ totalMonthlyCiro }}</p>
           </div>
           
           <div class="card hover:shadow-neon-turquoise/10 hover:border-ocean-700">
              <h3 class="text-gray-400 text-sm flex items-center gap-2">
                <svg class="w-4 h-4 text-neon-turquoise" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
                Son Satış Adedi
              </h3>
              <div v-if="isLoadingSales" class="h-10 mt-2 bg-dark-bg animate-pulse rounded"></div>
              <p v-else class="text-3xl font-bold text-neon-turquoise mt-2">{{ sales.length }}</p>
           </div>
         </div>

         <!-- Right Column (Export Module) -->
         <div class="md:col-span-4">
           <ReportExport />
         </div>
      </div>

      <!-- Recent Sales List -->
      <div class="card overflow-hidden">
        <h2 class="text-lg font-semibold mb-4 text-white border-b border-dark-border pb-4 px-2">
          Sisteme Düşen Son Satışlar
        </h2>
        
        <div v-if="isLoadingSales" class="py-8 text-center text-ocean-500 animate-pulse">
          Satışlar yükleniyor...
        </div>
        <div v-else-if="sales.length === 0" class="py-8 text-center text-gray-500">
          Hiç satış kaydı bulunamadı.
        </div>
        <div v-else class="overflow-x-auto w-full">
          <table class="w-full text-left text-sm whitespace-nowrap">
            <thead class="text-gray-400 border-b border-dark-border bg-dark-bg/50">
              <tr>
                <th class="py-3 px-4 font-medium">Tarih</th>
                <th class="py-3 px-4 font-medium">Personel ID</th>
                <th class="py-3 px-4 font-medium">Aktivite ID</th>
                <th class="py-3 px-4 font-medium text-right">Nakit</th>
                <th class="py-3 px-4 font-medium text-right">Kredi Kartı</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-dark-border">
              <TransitionGroup name="list">
                <tr v-for="sale in sales" :key="sale.id" class="hover:bg-ocean-900/20 transition-colors">
                  <td class="py-3 px-4 text-gray-300">{{ formatDate(sale.created_at) }}</td>
                  <td class="py-3 px-4 text-white">#{{ sale.added_by_user_id }}</td>
                  <td class="py-3 px-4 text-white">#{{ sale.activity_id }}</td>
                  <td class="py-3 px-4 text-right text-green-400 font-medium">{{ sale.cash_amount > 0 ? sale.cash_amount : '-' }}</td>
                  <td class="py-3 px-4 text-right text-ocean-400 font-medium">{{ sale.cc_amount > 0 ? sale.cc_amount : '-' }}</td>
                </tr>
              </TransitionGroup>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Modals -->
    <UserCreateModal :is-open="isUserModalOpen" @close="isUserModalOpen = false" />
    <ActivityCreateModal :is-open="isActivityModalOpen" @close="isActivityModalOpen = false" />
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/utils/axios'

// Components
import UserCreateModal from '@/components/Admin/UserCreateModal.vue'
import ActivityCreateModal from '@/components/Admin/ActivityCreateModal.vue'
import ReportExport from '@/components/Admin/ReportExport.vue'

const authStore = useAuthStore()
const router = useRouter()

const isMobileMenuOpen = ref(false)
const isUserModalOpen = ref(false)
const isActivityModalOpen = ref(false)

const sales = ref([])
const totalMonthlyCiro = ref("0.00")
const isLoadingSales = ref(true)
const isLoadingReports = ref(true)

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const openUserModal = () => {
  isMobileMenuOpen.value = false
  isUserModalOpen.value = true
}

const openActivityModal = () => {
  isMobileMenuOpen.value = false
  isActivityModalOpen.value = true
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const d = new Date(dateString)
  return d.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

const fetchData = async () => {
  try {
    isLoadingSales.value = true
    const salesRes = await api.get('/sales/', { params: { limit: 50 } })
    sales.value = salesRes.data || []
    
    isLoadingReports.value = true
    const date = new Date()
    const firstDay = new Date(date.getFullYear(), date.getMonth(), 1).toISOString().split('T')[0]
    const today = date.toISOString().split('T')[0]
    
    const reportsRes = await api.get('/reports/monthly', { 
      params: { start_date: firstDay, end_date: today } 
    })
    
    if (reportsRes.data && reportsRes.data.data && reportsRes.data.data.length > 0) {
      let total = 0
      reportsRes.data.data.forEach(item => {
         total += parseFloat(item.base_revenue || 0)
      })
      totalMonthlyCiro.value = total.toFixed(2)
    }

  } catch (error) {
    console.error('Data fetch error:', error)
  } finally {
    isLoadingSales.value = false
    isLoadingReports.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Hide scrollbar for neatness in responsive tables */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}
.overflow-x-auto::-webkit-scrollbar-track {
  background: transparent;
}
.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #2A4365;
  border-radius: 4px;
}
</style>
