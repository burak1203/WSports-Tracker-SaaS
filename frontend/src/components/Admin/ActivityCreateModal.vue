<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
    <div class="card w-full max-w-md relative bg-dark-surface border-neon-turquoise shadow-2xl shadow-neon-turquoise/20">
      <button @click="close" class="absolute top-4 right-4 text-gray-400 hover:text-white">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
      </button>
      
      <h2 class="text-xl font-bold text-white mb-6">Yeni Aktivite Ekle</h2>
      
      <form @submit.prevent="submitForm" class="space-y-4">
        <div>
          <label class="block text-sm text-gray-400 mb-1">Aktivite Adı</label>
          <input v-model="form.name" type="text" required class="w-full" placeholder="Örn: Parasailing" />
        </div>
        
        <div class="flex items-center gap-3 pt-2">
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="form.is_percentage_eligible" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-neon-turquoise"></div>
            <span class="ml-3 text-sm font-medium text-gray-300">Yüzdelik Hakedişe Dahil Mi?</span>
          </label>
        </div>

        <button type="submit" class="btn-neon w-full mt-6" :disabled="isSubmitting">
          <span v-if="!isSubmitting">Aktiviteyi Kaydet</span>
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
  name: '',
  is_percentage_eligible: false
})

const close = () => {
  emit('close')
  // reset
  form.name = ''
  form.is_percentage_eligible = false
}

const submitForm = async () => {
  isSubmitting.value = true
  try {
    await api.post('/activities/', form)
    toast.success('Aktivite başarıyla eklendi!')
    close()
  } catch (error) {
    console.error(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
