<template>
  <div class="min-h-screen flex bg-dark-bg text-gray-100 font-sans">
    
    <!-- Mobile Header & Hamburger -->
    <header class="md:hidden fixed top-0 left-0 right-0 z-40 bg-dark-surface border-b border-dark-border px-4 py-3 flex justify-between items-center shadow-lg">
      <h2 class="text-xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-neon-turquoise to-ocean-500 tracking-wide">WSPORTS TRACKER</h2>
      <button @click="isMobileMenuOpen = !isMobileMenuOpen" class="text-gray-300 hover:text-white p-2 rounded-md hover:bg-ocean-900/50 transition-colors">
        <svg v-if="!isMobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
    </header>

    <!-- Navigation Drawer -->
    <div v-if="isMobileMenuOpen" class="md:hidden fixed inset-0 z-30 bg-black/80 backdrop-blur-sm" @click="isMobileMenuOpen = false"></div>
    <aside :class="['fixed md:static inset-y-0 left-0 z-40 w-64 bg-dark-surface border-r border-dark-border transform transition-transform duration-300 ease-in-out md:translate-x-0 flex flex-col', isMobileMenuOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full']">
      <div class="p-6 hidden md:block">
        <h2 class="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-neon-turquoise to-ocean-500 tracking-wide">WSPORTS</h2>
        <p class="text-[10px] text-gray-500 mt-1 uppercase font-bold tracking-widest">{{ roleDisplayName }} PANELİ</p>
      </div>
      <div class="p-6 md:hidden mt-12 border-b border-dark-border">
        <p class="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Kullanıcı</p>
        <p class="text-white font-medium">{{ authStore.user?.full_name }}</p>
        <p class="text-xs text-neon-turquoise font-bold uppercase tracking-wider mt-2">{{ roleDisplayName }}</p>
      </div>
      
      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <!-- Route Links based on Role -->
        <router-link 
          v-if="canAccess(['admin', 'kasa', 'yuzdeci'])" 
          to="/dashboard" 
          active-class="bg-ocean-900/30 text-neon-turquoise border-l-4 border-neon-turquoise font-semibold"
          class="block px-4 py-3 rounded-r-lg text-sm text-gray-400 border-l-4 border-transparent hover:bg-dark-bg hover:text-white transition-all flex items-center gap-3"
          @click="isMobileMenuOpen = false"
        >
          <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path></svg>
          Dashboard
        </router-link>

        <router-link 
          v-if="canAccess(['admin', 'kasa', 'infocu'])" 
          to="/sales" 
          active-class="bg-ocean-900/30 text-neon-turquoise border-l-4 border-neon-turquoise font-semibold"
          class="block px-4 py-3 rounded-r-lg text-sm text-gray-400 border-l-4 border-transparent hover:bg-dark-bg hover:text-white transition-all flex items-center gap-3 mt-2"
          @click="isMobileMenuOpen = false"
        >
          <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          Satış Paneli
        </router-link>

        <router-link 
          v-if="canAccess(['admin', 'kasa'])" 
          to="/expenses" 
          active-class="bg-ocean-900/30 text-neon-turquoise border-l-4 border-neon-turquoise font-semibold"
          class="block px-4 py-3 rounded-r-lg text-sm text-gray-400 border-l-4 border-transparent hover:bg-dark-bg hover:text-white transition-all flex items-center gap-3 mt-2"
          @click="isMobileMenuOpen = false"
        >
          <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path></svg>
          Giderler
        </router-link>

        <router-link 
          v-if="canAccess(['admin'])" 
          to="/personnel-activity" 
          active-class="bg-ocean-900/30 text-neon-turquoise border-l-4 border-neon-turquoise font-semibold"
          class="block px-4 py-3 rounded-r-lg text-sm text-gray-400 border-l-4 border-transparent hover:bg-dark-bg hover:text-white transition-all flex items-center gap-3 mt-2"
          @click="isMobileMenuOpen = false"
        >
          <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
          Sistem Yönetimi
        </router-link>

        <router-link 
          v-if="canAccess(['admin', 'yuzdeci'])" 
          to="/reports" 
          active-class="bg-ocean-900/30 text-neon-turquoise border-l-4 border-neon-turquoise font-semibold"
          class="block px-4 py-3 rounded-r-lg text-sm text-gray-400 border-l-4 border-transparent hover:bg-dark-bg hover:text-white transition-all flex items-center gap-3 mt-2"
          @click="isMobileMenuOpen = false"
        >
          <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
          Raporlar
        </router-link>
      </nav>
      
      <div class="p-4 border-t border-dark-border">
        <button @click="logout" class="w-full text-left px-4 py-3 text-sm text-gray-400 hover:text-white flex items-center gap-3 transition-colors rounded-lg hover:bg-ocean-900/20">
          <svg class="w-5 h-5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
          Çıkış Yap
        </button>
      </div>
    </aside>

    <!-- Main Content Area - BUG FIX: using min-w-0 to prevent flex items from overflowing -->
    <main class="flex-1 min-w-0 p-4 pt-20 md:p-8 md:pt-8 overflow-y-auto">
       <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
       </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const isMobileMenuOpen = ref(false)

const roleDisplayName = computed(() => {
  const role = authStore.user?.role || ''
  return role.charAt(0).toUpperCase() + role.slice(1)
})

const canAccess = (allowedRoles) => {
  return allowedRoles.includes(authStore.user?.role)
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
