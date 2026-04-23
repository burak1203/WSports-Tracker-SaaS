<template>
  <div class="max-w-7xl mx-auto space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">Satış İşlemleri</h1>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <QuickSaleBasket />
      </div>
      
      <div class="lg:col-span-1 bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex items-center justify-center text-gray-400">
        Onay Bekleyenler Tablosu Buraya Gelecek...
      </div>
    </div>
  </div>
</template>

<script setup>
// Az önce diğer asistanın yazdırdığı bileşeni içeri aktarıyoruz
import QuickSaleBasket from '@/components/sales/QuickSaleBasket.vue'
</script>