<template>
  <div v-if="isOpen" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all">
      
      <div class="p-5 border-b border-gray-100 bg-red-50 flex justify-between items-center">
        <h3 class="font-bold text-red-700 flex items-center gap-2">
          <span class="text-xl">💸</span> Kasadan Gider / Masraf Çıkışı
        </h3>
        <button @click="close" class="text-red-400 hover:text-red-700 text-2xl font-black leading-none outline-none">&times;</button>
      </div>

      <form @submit.prevent="submitExpense" class="p-6 space-y-5">
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-1.5">Gider Kategorisi</label>
          <select v-model="form.category" required class="w-full p-2.5 bg-slate-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition-all font-medium text-slate-700">
            <option value="Yakıt / Benzin">Yakıt / Benzin</option>
            <option value="Yemek / İkram">Yemek / İkram</option>
            <option value="Maaş / Avans">Maaş / Avans</option>
            <option value="Müşteri İadesi">Müşteri İadesi</option>
            <option value="Diğer Masraflar">Diğer Masraflar</option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-bold text-slate-700 mb-1.5">Açıklama <span class="text-gray-400 font-normal">(Opsiyonel)</span></label>
          <input v-model="form.description" type="text" placeholder="Örn: Tekne için 50lt benzin" class="w-full p-2.5 bg-slate-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none transition-all text-slate-700">
        </div>

        <div class="grid grid-cols-12 gap-3">
          <div class="col-span-5">
            <label class="block text-sm font-bold text-slate-700 mb-1.5">Tutar</label>
            <input v-model.number="form.amount" type="number" step="0.01" min="0.1" required placeholder="0.00" class="w-full p-2.5 bg-slate-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none font-bold text-slate-800 text-right">
          </div>
          <div class="col-span-3">
            <label class="block text-sm font-bold text-slate-700 mb-1.5">Döviz</label>
            <select v-model="form.currency" class="w-full p-2.5 bg-slate-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none font-semibold text-slate-700">
              <option value="try">TL (₺)</option>
              <option value="eur">EUR (€)</option>
              <option value="usd">USD ($)</option>
              <option value="gbp">GBP (£)</option>
            </select>
          </div>
          <div class="col-span-4">
            <label class="block text-sm font-bold text-slate-700 mb-1.5">Kasa/Ödeme</label>
            <select v-model="form.method" class="w-full p-2.5 bg-slate-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 outline-none font-semibold text-slate-700">
              <option value="cash">Nakit</option>
              <option value="cc">K. Kartı</option>
            </select>
          </div>
        </div>

        <button type="submit" :disabled="isSubmitting" class="w-full bg-red-600 text-white font-bold py-3.5 rounded-lg hover:bg-red-700 transition-all disabled:opacity-50 mt-2 shadow-sm shadow-red-200">
          {{ isSubmitting ? 'Kayıt İşleniyor...' : 'Kasadan Masraf Çık' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from '@/utils/axios'

// Dışarıdan modalı açıp kapatmak için state
const isOpen = ref(false)
const isSubmitting = ref(false)

const form = ref({
  category: 'Yakıt / Benzin',
  description: '',
  amount: null,
  currency: 'try',
  method: 'cash'
})

// Modalı açan fonksiyon
const open = () => {
  isOpen.value = true
  form.value = { category: 'Yakıt / Benzin', description: '', amount: null, currency: 'try', method: 'cash' }
}

const close = () => {
  isOpen.value = false
}

const submitExpense = async () => {
  isSubmitting.value = true
  
  // Backend'in beklediği 8 sütunlu (flat) şemayı 0'larla hazırlıyoruz
  const payload = {
    category: form.value.category,
    description: form.value.description,
    try_cash: 0, eur_cash: 0, usd_cash: 0, gbp_cash: 0,
    try_cc: 0, eur_cc: 0, usd_cc: 0, gbp_cc: 0,
    eur_rate: 35.00, // Not: Kur API'si entegre edildiğinde buralar store'dan gelecek
    usd_rate: 32.50,
    gbp_rate: 40.00
  }

  // Kullanıcının seçtiği döviz ve ödeme yöntemini dinamik olarak birleştirip (örn: eur_cash) ilgili kolona tutarı basıyoruz
  const dynamicKey = `${form.value.currency}_${form.value.method}`
  payload[dynamicKey] = parseFloat(form.value.amount)

  try {
    await axios.post('/expenses/', payload)
    close()
    alert('Masraf başarıyla kasadan düşüldü.')
  } catch (error) {
    alert(error.response?.data?.detail || 'Masraf kaydedilirken bir hata oluştu.')
  } finally {
    isSubmitting.value = false
  }
}

// Parent bileşenin (SalesView) bu fonksiyonlara erişebilmesi için dışa aktarıyoruz
defineExpose({ open, close })
</script>