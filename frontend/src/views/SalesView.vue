<template>
  <div class="max-w-7xl mx-auto space-y-6 h-[calc(100vh-8rem)]">
    
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">Satış İşlemleri</h1>
      <button @click="openExpenseModal" class="bg-red-50 text-red-600 font-bold px-4 py-2 rounded-lg border border-red-200 hover:bg-red-100 hover:border-red-300 transition-all shadow-sm">
        💸 Kasadan Masraf Çık
      </button>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full pb-6">
      <div class="lg:col-span-2">
        <QuickSaleBasket @sale-added="handleNewSale" />
      </div>
      <div class="lg:col-span-1 h-[600px] lg:h-auto">
        <PendingSalesTable ref="pendingTableRef" />
      </div>
    </div>

    <ExpenseModal ref="expenseModalRef" />

  </div>
</template>

<script setup>
import { ref } from 'vue'
import QuickSaleBasket from '@/components/sales/QuickSaleBasket.vue'
import PendingSalesTable from '@/components/sales/PendingSalesTable.vue'
import ExpenseModal from '@/components/sales/ExpenseModal.vue' // EKLENDİ

const pendingTableRef = ref(null)
const expenseModalRef = ref(null) // EKLENDİ

const handleNewSale = () => {
  if (pendingTableRef.value) pendingTableRef.value.fetchPendingSales()
}

// Modalı açan tetikleyici fonksiyon (EKLENDİ)
const openExpenseModal = () => {
  if (expenseModalRef.value) {
    expenseModalRef.value.open()
  }
}
</script>
