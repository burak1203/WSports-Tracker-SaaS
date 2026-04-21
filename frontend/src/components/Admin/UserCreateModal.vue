<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
    <div class="card w-full max-w-md relative bg-dark-surface border-ocean-700 shadow-2xl shadow-ocean-900/50">
      <button @click="close" class="absolute top-4 right-4 text-gray-400 hover:text-white">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
      
      <h2 class="text-xl font-bold text-white mb-6">Yeni Personel Ekle</h2>
      
      <form @submit.prevent="submitForm" class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">Ad Soyad</label>
          <input v-model="form.full_name" type="text" required class="w-full" placeholder="Örn: Ahmet Yılmaz" />
        </div>
        
        <div>
          <label class="block text-sm text-gray-400 mb-1">Şifre</label>
          <input v-model="form.password" type="password" required class="w-full" placeholder="••••••••" />
        </div>

        <div>
          <label class="block text-sm text-gray-400 mb-1">Rol</label>
          <select v-model="form.role" required class="w-full">
            <option value="admin">Admin</option>
            <option value="infocu">İnfocu</option>
            <option value="kasa">Kasa</option>
            <option value="yuzdeci">Yüzdeci</option>
          </select>
        </div>

        <!-- Target Revenue only for infocu -->
        <div v-if="form.role === 'infocu'">
          <label class="block text-sm text-gray-400 mb-1">Hedef Ciro (Opsiyonel)</label>
          <input v-model="form.target_revenue" type="number" step="0.01" min="0" class="w-full" placeholder="0.00" />
        </div>

        <button type="submit" class="btn-primary w-full mt-6" :disabled="isSubmitting">
          <span v-if="!isSubmitting">Personeli Kaydet</span>
          <span v-else class="animate-pulse">Kaydediliyor...</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '@/utils/axios'
import { useToast } from 'vue-toastification'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])
const toast = useToast()
const isSubmitting = ref(false)

const form = reactive({
  full_name: '',
  password: '',
  role: 'infocu',
  target_revenue: ''
})

const close = () => {
  emit('close')
  // reset
  form.full_name = ''
  form.password = ''
  form.role = 'infocu'
  form.target_revenue = ''
}

const submitForm = async () => {
  isSubmitting.value = true
  try {
    const payload = { ...form }
    if (payload.role !== 'infocu' || !payload.target_revenue) {
      payload.target_revenue = null
    } else {
      payload.target_revenue = parseFloat(payload.target_revenue)
    }

    await api.post('/users/', payload)
    toast.success('Personel başarıyla eklendi!')
    close()
  } catch (error) {
    console.error(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
