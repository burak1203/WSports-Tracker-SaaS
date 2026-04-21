<template>
  <div class="w-full">
    <header class="mb-8">
      <h1 class="text-3xl font-extrabold text-white tracking-tight">Giderler</h1>
      <p class="text-sm text-gray-400 mt-1">İşletmenizin tüm masraflarını detaylı olarak kaydedin ve takip edin.</p>
    </header>

    <div class="flex flex-col gap-8 w-full">
      
      <!-- Expense Form -->
      <div class="w-full bg-dark-surface border border-dark-border rounded-xl shadow-xl p-6">
        <h2 class="text-lg font-bold text-white mb-6 border-b border-dark-border pb-3 flex items-center gap-2">
          <svg class="w-5 h-5 text-neon-turquoise" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
          Yeni Gider Ekle
        </h2>
        
        <form @submit.prevent="submitExpense" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
            
            <div class="md:col-span-4">
              <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Kategori Seçin</label>
              <div class="relative">
                <select v-model="form.category" required class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white appearance-none focus:outline-none focus:border-neon-turquoise focus:ring-1 focus:ring-neon-turquoise transition-all">
                  <option value="" disabled>Seçiniz...</option>
                  <option value="Yakıt">Yakıt / Tekne</option>
                  <option value="Mutfak">Mutfak / Yemek</option>
                  <option value="Personel">Personel / Avans</option>
                  <option value="Bakım">Bakım & Tamir</option>
                  <option value="Kategori Dışı">Kategori Dışı</option>
                </select>
                <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-400">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </div>
              </div>
            </div>

            <div class="md:col-span-8">
              <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Açıklama (İsteğe Bağlı)</label>
              <input v-model="form.description" type="text" class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" placeholder="Detay bilgi..." />
            </div>

            <div class="md:col-span-12 grid grid-cols-1 md:grid-cols-4 gap-4">
              <!-- Para Birimi Seçimi -->
              <div>
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Para Birimi</label>
                <div class="relative">
                  <select v-model="form.currency" required class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white appearance-none focus:outline-none focus:border-neon-turquoise transition-all">
                    <option value="TRY">₺ TL</option>
                    <option value="EUR">€ Euro</option>
                    <option value="USD">$ USD</option>
                    <option value="GBP">£ Sterlin</option>
                  </select>
                  <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </div>
                </div>
              </div>

              <!-- Nakit -->
              <div class="md:col-span-2">
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Nakit Ödeme</label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <span class="text-green-500 font-bold">{{ currencySymbol }}</span>
                  </div>
                  <input v-model="form.cash_amount" type="number" step="0.01" min="0" class="w-full bg-dark-bg border border-dark-border rounded-lg pl-8 pr-4 py-3 text-white focus:outline-none focus:border-green-500 transition-all" placeholder="0.00" />
                </div>
              </div>

              <!-- Kredi -->
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

          <div class="flex justify-end pt-2">
            <button type="submit" class="bg-gradient-to-r from-ocean-600 to-neon-turquoise hover:from-ocean-500 hover:to-neon-turquoise text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-neon-turquoise/20 transform transition-all hover:-translate-y-0.5" :disabled="isSubmitting">
              <span v-if="!isSubmitting" class="flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                + Ekle
              </span>
              <span v-else class="flex items-center gap-2 animate-pulse">
                İşleniyor...
              </span>
            </button>
          </div>
        </form>
      </div>

      <!-- Expenses List Table -->
      <div class="w-full bg-dark-surface border border-dark-border rounded-xl shadow-xl overflow-hidden">
        <div class="p-6 border-b border-dark-border bg-dark-bg/30">
          <h2 class="text-lg font-bold text-white">Bu Günün Giderleri</h2>
        </div>
        
        <div v-if="isLoading" class="py-12 text-center">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-neon-turquoise"></div>
        </div>
        
        <div v-else-if="expenses.length === 0" class="py-12 text-center text-gray-500">
          Henüz kayıt yok
        </div>
        
        <div v-else class="overflow-x-auto w-full">
          <table class="w-full text-left text-sm whitespace-nowrap">
            <thead class="text-xs text-gray-400 uppercase tracking-wider bg-dark-bg/80">
              <tr>
                <th class="py-4 px-6 font-semibold">Tarih</th>
                <th class="py-4 px-6 font-semibold">Kategori</th>
                <th class="py-4 px-6 font-semibold text-right">Para Birimi</th>
                <th class="py-4 px-6 font-semibold text-right">Nakit</th>
                <th class="py-4 px-6 font-semibold text-right">Kredi Kartı</th>
                <th class="py-4 px-6 font-semibold">Açıklama</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-dark-border">
              <tr v-for="exp in expenses" :key="exp.id" class="hover:bg-ocean-900/10 transition-colors">
                <td class="py-4 px-6 text-gray-300">{{ formatDate(exp.created_at) }}</td>
                <td class="py-4 px-6 text-white font-medium">{{ exp.category }}</td>
                <td class="py-4 px-6 text-right text-gray-400">{{ exp.currency }}</td>
                <td class="py-4 px-6 text-right text-red-400 font-bold">{{ exp.cash_amount > 0 ? '-' + formatCurrency(exp.cash_amount) : '' }}</td>
                <td class="py-4 px-6 text-right text-orange-400 font-bold">{{ exp.cc_amount > 0 ? '-' + formatCurrency(exp.cc_amount) : '' }}</td>
                <td class="py-4 px-6 text-gray-400 truncate max-w-[200px]">{{ exp.description || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/utils/axios'
import { useToast } from 'vue-toastification'

const toast = useToast()
const expenses = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)

const form = reactive({
  category: '',
  description: '',
  cash_amount: '',
  cc_amount: '',
  currency: 'TRY'
})

const currencySymbol = computed(() => {
  if (form.currency === 'EUR') return '€'
  if (form.currency === 'USD') return '$'
  if (form.currency === 'GBP') return '£'
  return '₺'
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  const d = new Date(dateString)
  return d.toLocaleDateString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return new Intl.NumberFormat('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount)
}

const fetchExpenses = async () => {
  try {
    isLoading.value = true
    const res = await api.get('/expenses/')
    expenses.value = res.data || []
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const submitExpense = async () => {
  if (!form.cash_amount && !form.cc_amount) {
    toast.warning('Nakit veya Kredi Kartı tutarı girmelisiniz.')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      category: form.category,
      description: form.description,
      currency: form.currency,
      cash_amount: form.cash_amount ? parseFloat(form.cash_amount) : 0,
      cc_amount: form.cc_amount ? parseFloat(form.cc_amount) : 0
    }
    
    await api.post('/expenses/', payload)
    toast.success('Gider eklendi!')
    
    form.cash_amount = ''
    form.cc_amount = ''
    form.description = ''
    
    fetchExpenses()
  } catch (error) {
    console.error(error)
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  fetchExpenses()
})
</script>
