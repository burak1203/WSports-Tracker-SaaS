<template>
  <div class="max-w-7xl mx-auto space-y-0">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-slate-800">Sistem & Kurum Yönetimi</h1>
    </div>

    <div class="flex border-b border-gray-200 bg-white rounded-t-xl px-4 pt-4 shadow-sm">
      <button
        @click="activeTab = 'users'"
        :class="[
          activeTab === 'users' 
            ? 'border-blue-600 text-blue-600' 
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 
          'whitespace-nowrap py-4 px-6 border-b-2 font-bold text-sm transition-colors'
        ]"
      >
        👥 Kullanıcılar & Personel
      </button>
      <button
        @click="activeTab = 'activities'"
        :class="[
          activeTab === 'activities' 
            ? 'border-blue-600 text-blue-600' 
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 
          'whitespace-nowrap py-4 px-6 border-b-2 font-bold text-sm transition-colors'
        ]"
      >
        🏄 Aktiviteler & Komisyonlar
      </button>
    </div>

    <div class="bg-white p-6 rounded-b-xl shadow-sm border border-t-0 border-gray-100 min-h-[500px]">
      <UserManagement v-if="activeTab === 'users'" />
      <ActivityManagement v-if="activeTab === 'activities'" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Alt bileşenleri içeri aktarıyoruz (Bunları şimdi oluşturacaksın)
import UserManagement from '@/components/admin/UserManagement.vue'
import ActivityManagement from '@/components/admin/ActivityManagement.vue'

const activeTab = ref('users') // Varsayılan olarak kullanıcılar sekmesi açık
</script>