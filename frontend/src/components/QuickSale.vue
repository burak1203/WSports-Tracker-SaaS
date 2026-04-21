<template>
  <form @submit.prevent="submitSale" class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
      
      <!-- Activity Selection -->
      <div class="md:col-span-4">
        <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Aktivite Seçin</label>
        <div class="relative">
          <select v-model="form.activity_id" required class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white appearance-none focus:outline-none focus:border-neon-turquoise focus:ring-1 focus:ring-neon-turquoise transition-all">
            <option value="" disabled>Aktivite Seçiniz...</option>
            <option v-for="act in activities" :key="act.id" :value="act.id">{{ act.name }}</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </div>
        </div>
      </div>

      <!-- Currency Selection -->
      <div class="md:col-span-2">
        <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Para Birimi</label>
        <div class="relative">
          <select v-model="form.currency" required class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white appearance-none focus:outline-none focus:border-neon-turquoise transition-all">
            <option value="EUR">€ Euro</option>
            <option value="USD">$ USD</option>
            <option value="GBP">£ Sterlin</option>
            <option value="TRY">₺ TL</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </div>
        </div>
      </div>

      <!-- Amounts -->
      <div class="md:col-span-6 grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Nakit Tutar</label>
          <div class="relative">
             <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span class="text-green-500 font-bold">{{ currencySymbol }}</span>
             </div>
             <input v-model="form.cash_amount" type="number" step="0.01" min="0" class="w-full bg-dark-bg border border-dark-border rounded-lg pl-8 pr-4 py-3 text-white focus:outline-none focus:border-green-500 transition-all" placeholder="0.00" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Kredi Kartı</label>
          <div class="relative">
             <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <span class="text-ocean-400 font-bold">{{ currencySymbol }}</span>
             </div>
             <input v-model="form.cc_amount" type="number" step="0.01" min="0" class="w-full bg-dark-bg border border-dark-border rounded-lg pl-8 pr-4 py-3 text-white focus:outline-none focus:border-ocean-500 transition-all" placeholder="0.00" />
          </div>
        </div>
      </div>

    </div>

    <!-- Submit Area -->
    <div class="flex justify-end pt-2">
      <button type="submit" class="bg-gradient-to-r from-ocean-600 to-neon-turquoise hover:from-ocean-500 hover:to-neon-turquoise text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-neon-turquoise/20 transform transition-all hover:-translate-y-0.5" :disabled="isSubmitting">
        <span v-if="!isSubmitting" class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
          Sisteme İşle
        </span>
        <span v-else class="flex items-center gap-2 animate-pulse">
          <svg class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          İşleniyor...
        </span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/utils/axios'
import { useToast } from 'vue-toastification'

const emit = defineEmits(['sale-added'])
const toast = useToast()
const isSubmitting = ref(false)
const activities = ref([])

const form = reactive({
  activity_id: '',
  cash_amount: '',
  cc_amount: '',
  currency: 'EUR'
})

const currencySymbol = computed(() => {
  if (form.currency === 'EUR') return '€'
  if (form.currency === 'USD') return '$'
  if (form.currency === 'GBP') return '£'
  return '₺'
})

const submitSale = async () => {
  if (!form.cash_amount && !form.cc_amount) {
    toast.warning('Lütfen nakit veya kredi kartı tutarı giriniz.')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      activity_id: parseInt(form.activity_id),
      currency: form.currency,
      cash_amount: form.cash_amount ? parseFloat(form.cash_amount) : 0,
      cc_amount: form.cc_amount ? parseFloat(form.cc_amount) : 0
    }
    
    await api.post('/sales/', payload)
    toast.success('Satış başarıyla eklendi!')
    
    // Reset form amounts
    form.cash_amount = ''
    form.cc_amount = ''
    
    emit('sale-added')
  } catch (error) {
    // Error is handled globally by interceptor, but we can catch local ones
    console.error(error)
  } finally {
    isSubmitting.value = false
  }
}

const fetchActivities = async () => {
  try {
    const res = await api.get('/activities/')
    activities.value = res.data || []
  } catch(e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchActivities()
})
</script>
