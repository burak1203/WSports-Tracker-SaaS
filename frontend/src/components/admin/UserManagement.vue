<template>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
    
    <div class="lg:col-span-1 bg-slate-50 p-5 rounded-xl border border-slate-200 h-fit transition-all" :class="{'ring-2 ring-orange-400': editingUserId}">
      <div class="flex justify-between items-center mb-4 border-b pb-2">
        <h2 class="text-lg font-bold" :class="editingUserId ? 'text-orange-600' : 'text-slate-800'">
          {{ editingUserId ? 'Personel Düzenle' : 'Yeni Personel Ekle' }}
        </h2>
        <button v-if="editingUserId" @click="cancelEdit" class="text-xs text-gray-500 hover:text-gray-700 underline">İptal Et</button>
      </div>
      
      <form @submit.prevent="submitUser" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Ad Soyad</label>
          <input v-model="form.full_name" type="text" required class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none">
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Şifre <span v-if="editingUserId" class="text-xs text-gray-400 font-normal">(Değiştirmeyecekseniz boş bırakın)</span></label>
          <input v-model="form.password" type="password" :required="!editingUserId" class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none">
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">Sistem Rolü</label>
          <select v-model="form.role" required class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none">
            <option value="kasa">Kasa</option>
            <option value="infocu">İnfocu</option>
            <option value="yuzdeci">Yüzdelikçi</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <div v-if="form.role === 'infocu'" class="p-3 bg-blue-50 border border-blue-100 rounded">
          <label class="block text-sm font-medium text-blue-800 mb-1">Aylık Ciro Hedefi (₺)</label>
          <input v-model.number="form.target_revenue" type="number" min="0" class="w-full p-2 border border-blue-300 rounded focus:ring-2 focus:ring-blue-500 outline-none">
        </div>

        <div v-if="errorMsg" class="p-2 bg-red-100 text-red-700 text-sm rounded border border-red-200">
          {{ errorMsg }}
        </div>

        <button type="submit" :disabled="isSubmitting" class="w-full font-bold py-2.5 rounded transition-colors disabled:opacity-50" :class="editingUserId ? 'bg-orange-600 hover:bg-orange-700 text-white' : 'bg-slate-800 hover:bg-slate-700 text-white'">
          {{ isSubmitting ? 'İşleniyor...' : (editingUserId ? 'Değişiklikleri Kaydet' : 'Personeli Kaydet') }}
        </button>
      </form>
    </div>

    <div class="lg:col-span-2">
      <div class="flex justify-between items-center mb-4 border-b pb-2">
        <h2 class="text-lg font-bold text-slate-800">Aktif Personel Listesi</h2>
        <button @click="fetchUsers" class="text-sm text-blue-600 hover:text-blue-800">↻ Yenile</button>
      </div>

      <div v-if="isLoading" class="text-center py-8 text-gray-500">Yükleniyor...</div>
      
      <div v-else class="overflow-x-auto bg-white border border-gray-200 rounded-lg shadow-sm">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-100 text-slate-600 text-sm">
              <th class="p-3 border-b">ID</th>
              <th class="p-3 border-b">Kullanıcı</th>
              <th class="p-3 border-b">Rol</th>
              <th class="p-3 border-b text-right">İşlemler</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="users.length === 0">
              <td colspan="4" class="p-4 text-center text-gray-500">Sistemde personel yok.</td>
            </tr>
            <tr v-for="user in users" :key="user.id" class="border-b hover:bg-slate-50 transition-colors">
              <td class="p-3 text-slate-500 text-sm">#{{ user.id }}</td>
              <td class="p-3 font-semibold text-slate-800">{{ user.full_name }}</td>
              <td class="p-3"><span class="px-2 py-1 text-xs font-bold rounded uppercase tracking-wider bg-slate-200 text-slate-700">{{ user.role }}</span></td>
              <td class="p-3 text-right flex justify-end gap-2">
                <button @click="editUser(user)" class="text-blue-600 hover:text-blue-800 text-sm font-semibold px-2 py-1 bg-blue-50 rounded">Düzenle</button>
                
                <button v-if="user.id !== currentUserId" @click="deleteUser(user.id, user.full_name)" class="text-red-500 hover:text-red-700 text-sm font-semibold px-2 py-1 bg-red-50 rounded">İşten Çıkar</button>
                <span v-else class="text-xs text-gray-400 font-medium px-2 py-1">Siz</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/utils/axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const users = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMsg = ref('')

// YENİ: Edit State
const editingUserId = ref(null)

const form = ref({ full_name: '', password: '', role: 'kasa', target_revenue: null })

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const response = await axios.get('/users/')
    users.value = response.data
  } catch (error) {
    errorMsg.value = "Listeyi çekerken hata oluştu."
  } finally {
    isLoading.value = false
  }
}

// YENİ: Edit Moduna Geçiş
const editUser = (user) => {
  editingUserId.value = user.id
  form.value = {
    full_name: user.full_name,
    password: '', // Şifre boş gelir, girilmezse değişmez
    role: user.role,
    target_revenue: user.target_revenue || null
  }
}

const cancelEdit = () => {
  editingUserId.value = null
  form.value = { full_name: '', password: '', role: 'kasa', target_revenue: null }
  errorMsg.value = ''
}

// GÜNCELLENDİ: Hem Ekleme Hem Güncelleme Yapar
const submitUser = async () => {
  isSubmitting.value = true
  errorMsg.value = ''
  
  const payload = {
    full_name: form.value.full_name,
    role: form.value.role,
    target_revenue: form.value.role === 'infocu' ? form.value.target_revenue : null
  }
  
  // Şifre girildiyse payload'a ekle (Düzenlerken boş bırakılmış olabilir)
  if (form.value.password) {
    payload.password = form.value.password
  }

  try {
    if (editingUserId.value) {
      // GÜNCELLEME (PUT)
      await axios.put(`/users/${editingUserId.value}`, payload)
    } else {
      // YENİ EKLEME (POST)
      await axios.post('/users/', payload)
    }
    
    cancelEdit()
    await fetchUsers()
  } catch (error) {
    errorMsg.value = error.response?.data?.detail || "İşlem başarısız oldu."
  } finally {
    isSubmitting.value = false
  }
}

const deleteUser = async (id, name) => {
  if(!confirm(`${name} isimli personeli silmek istediğinize emin misiniz?`)) return
  try {
    await axios.delete(`/users/${id}`)
    await fetchUsers()
  } catch (error) {
    alert("Silme işlemi başarısız oldu.")
  }
}

onMounted(() => { fetchUsers() })
</script>