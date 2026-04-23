<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-center justify-between mb-6 border-b border-gray-100 pb-4">
      <h2 class="text-lg font-bold text-slate-800">Hızlı Satış & Gelir Girişi</h2>
      <div class="text-sm text-gray-500 font-medium bg-gray-50 px-3 py-1 rounded-md">
        Kur: 1€ = {{ coreStore.exchangeRates.eur }}₺
      </div>
    </div>

    <form @submit.prevent="submitSale">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">Aktivite *</label>
          <select 
            v-model="form.activity_id" 
            required
            class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          >
            <option value="" disabled>— Aktivite Seçin —</option>
            <option v-for="act in coreStore.activities" :key="act.id" :value="act.id">
              {{ act.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 mb-2">İnfocu (Opsiyonel)</label>
          <select 
            v-model="form.infocu_id"
            class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
          >
            <option value="">— Kasadan Direkt Satış —</option>
            <option v-for="info in coreStore.infocus" :key="info.id" :value="info.id">
              {{ info.full_name }}
            </option>
          </select>
        </div>
      </div>

      <div class="mb-6 bg-slate-50 p-4 rounded-xl border border-slate-200">
        <div class="flex items-center justify-between mb-4">
          <label class="block text-sm font-bold text-slate-700">Ödeme Sepeti *</label>
          <button 
            type="button" 
            @click="addBasketRow"
            class="text-sm bg-blue-100 text-blue-700 font-semibold px-3 py-1.5 rounded hover:bg-blue-200 transition-colors"
          >
            + Yeni Tutar Ekle
          </button>
        </div>

        <div class="space-y-3">
          <div 
            v-for="(item, index) in basket" 
            :key="item.id"
            class="flex items-center gap-3 bg-white p-2 rounded-lg border border-gray-200 shadow-sm"
          >
            <select v-model="item.currency" class="w-24 px-3 py-2 bg-gray-50 border border-gray-200 rounded outline-none focus:border-blue-500">
              <option value="try">₺ TL</option>
              <option value="eur">€ EUR</option>
              <option value="usd">$ USD</option>
              <option value="gbp">£ GBP</option>
            </select>

            <input 
              type="number" 
              v-model="item.amount" 
              min="0" 
              step="0.01" 
              placeholder="0.00" 
              required
              class="flex-1 px-3 py-2 border border-gray-200 rounded outline-none focus:border-blue-500 text-right font-medium"
            >

            <select v-model="item.method" class="w-32 px-3 py-2 bg-gray-50 border border-gray-200 rounded outline-none focus:border-blue-500">
              <option value="cash">Nakit</option>
              <option value="cc">Kredi Kartı</option>
            </select>

            <button 
              type="button" 
              @click="removeBasketRow(index)"
              class="w-10 h-10 flex items-center justify-center text-red-500 hover:bg-red-50 rounded transition-colors"
              :disabled="basket.length === 1"
              :class="{'opacity-50 cursor-not-allowed': basket.length === 1}"
            >
              ✕
            </button>
          </div>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-200 flex justify-end gap-4 text-sm">
          <div v-if="totals.try > 0" class="font-semibold text-slate-700">TL: <span class="text-blue-600">{{ totals.try.toFixed(2) }}₺</span></div>
          <div v-if="totals.eur > 0" class="font-semibold text-slate-700">EUR: <span class="text-green-600">{{ totals.eur.toFixed(2) }}€</span></div>
          <div v-if="totals.usd > 0" class="font-semibold text-slate-700">USD: <span class="text-gray-600">{{ totals.usd.toFixed(2) }}$</span></div>
          <div v-if="totals.gbp > 0" class="font-semibold text-slate-700">GBP: <span class="text-purple-600">{{ totals.gbp.toFixed(2) }}£</span></div>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <button 
          type="submit" 
          :disabled="isSubmitting || totalBasketAmount <= 0"
          class="flex-1 bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isSubmitting ? 'Kaydediliyor...' : 'Satışı Tamamla ve Sepeti Onayla' }}
        </button>
      </div>

      <div v-if="successMessage" class="mt-4 p-3 bg-green-50 text-green-700 border border-green-200 rounded-lg text-center font-medium">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="mt-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg text-center font-medium">
        {{ errorMessage }}
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCoreStore } from '@/stores/core'
import axios from '@/utils/axios'

const coreStore = useCoreStore()

// State
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const form = ref({
  activity_id: '',
  infocu_id: ''
})

// Sepet (Başlangıçta tek boş satır)
const basket = ref([
  { id: Date.now(), currency: 'try', amount: null, method: 'cash' }
])

// Actions
const addBasketRow = () => {
  basket.value.push({ id: Date.now(), currency: 'eur', amount: null, method: 'cash' })
}

const removeBasketRow = (index) => {
  if (basket.value.length > 1) {
    basket.value.splice(index, 1)
  }
}

// Computeds
const totals = computed(() => {
  const t = { try: 0, eur: 0, usd: 0, gbp: 0 }
  basket.value.forEach(item => {
    if (item.amount) t[item.currency] += parseFloat(item.amount)
  })
  return t
})

const totalBasketAmount = computed(() => {
  return Object.values(totals.value).reduce((a, b) => a + b, 0)
})

// Backend'e Gönderim
const submitSale = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  if (totalBasketAmount.value <= 0) {
    errorMessage.value = 'Sepet tutarı 0 olamaz!'
    return
  }

  isSubmitting.value = true

  // 1. Backend'in beklediği Düz (Flat) yapıyı oluştur
  const payload = {
    activity_id: form.value.activity_id,
    added_by_user_id: form.value.infocu_id || null, // İnfocu seçildiyse onu gönder
    try_cash: 0, eur_cash: 0, usd_cash: 0, gbp_cash: 0,
    try_cc: 0, eur_cc: 0, usd_cc: 0, gbp_cc: 0,
    eur_rate: coreStore.exchangeRates.eur,
    usd_rate: coreStore.exchangeRates.usd,
    gbp_rate: coreStore.exchangeRates.gbp
  }

  // 2. Dinamik sepeti map'le (Örn: currency='eur', method='cc' => eur_cc)
  basket.value.forEach(item => {
    if (item.amount > 0) {
      const fieldName = `${item.currency}_${item.method}`
      payload[fieldName] += parseFloat(item.amount)
    }
  })

  try {
    await axios.post('/sales/', payload)
    successMessage.value = 'Satış başarıyla sepete işlendi! (Durum: Beklemede)'
    
    // Formu sıfırla
    form.value.activity_id = ''
    form.value.infocu_id = ''
    basket.value = [{ id: Date.now(), currency: 'try', amount: null, method: 'cash' }]
    
    setTimeout(() => { successMessage.value = '' }, 3000)
    
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Satış kaydedilirken bir hata oluştu.'
  } finally {
    isSubmitting.value = false
  }
}
</script>