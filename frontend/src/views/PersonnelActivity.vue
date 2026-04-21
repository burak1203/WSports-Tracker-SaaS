<template>
  <div class="w-full">
    <header class="mb-8">
      <h1 class="text-3xl font-extrabold text-white tracking-tight">Sistem Yönetimi</h1>
      <p class="text-sm text-gray-400 mt-1">Sisteme yeni kullanıcı veya aktivite tipi tanımlayın.</p>
    </header>

    <div class="bg-dark-surface border border-dark-border rounded-xl shadow-xl overflow-hidden">
      
      <!-- Tab Header -->
      <div class="flex border-b border-dark-border bg-dark-bg/50">
        <button 
          @click="activeTab = 'users'" 
          :class="['px-8 py-4 text-sm font-bold tracking-wider uppercase transition-colors', activeTab === 'users' ? 'text-neon-turquoise border-b-2 border-neon-turquoise bg-ocean-900/10' : 'text-gray-500 hover:text-gray-300']"
        >
          Kullanıcı İşlemleri
        </button>
        <button 
          @click="activeTab = 'activities'" 
          :class="['px-8 py-4 text-sm font-bold tracking-wider uppercase transition-colors', activeTab === 'activities' ? 'text-neon-turquoise border-b-2 border-neon-turquoise bg-ocean-900/10' : 'text-gray-500 hover:text-gray-300']"
        >
          Aktiviteler
        </button>
      </div>

      <!-- Tab Content -->
      <div class="p-6 md:p-10">
        
        <!-- Users Form -->
        <div v-show="activeTab === 'users'" class="max-w-2xl">
          <div class="mb-8 border-b border-dark-border pb-4">
            <h2 class="text-xl font-bold text-white flex items-center gap-3">
               <svg class="w-6 h-6 text-ocean-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
               Yeni Personel Ekle
            </h2>
            <p class="text-xs text-gray-400 mt-1">Sisteme erişebilecek yeni bir hesap oluşturun.</p>
          </div>

          <form @submit.prevent="submitUser" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Ad Soyad *</label>
                <input v-model="userForm.full_name" type="text" required class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" placeholder="Örn: Ahmet Yılmaz" />
              </div>
              
              <div>
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Sistem Rolü *</label>
                <div class="relative">
                  <select v-model="userForm.role" required class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white appearance-none focus:outline-none focus:border-neon-turquoise transition-all">
                    <option value="" disabled>Rol Seçin</option>
                    <option value="infocu">İnfocu (Satış Yapan)</option>
                    <option value="kasa">Kasa (Finans)</option>
                    <option value="yuzdeci">Yüzdelikçi (Paydaş)</option>
                    <option value="admin">Sistem Yöneticisi</option>
                  </select>
                  <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Şifre *</label>
                <input v-model="userForm.password" type="text" required class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" placeholder="Hesap şifresi belirleyin" />
              </div>

              <div v-if="userForm.role === 'infocu'" class="md:col-span-2">
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Hedef Ciro (Opsiyonel)</label>
                <input v-model="userForm.target_revenue" type="number" step="0.01" class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" placeholder="Örn: 50000" />
              </div>
            </div>

            <div class="pt-4 flex justify-end">
              <button type="submit" class="bg-gradient-to-r from-ocean-600 to-neon-turquoise hover:from-ocean-500 hover:to-neon-turquoise text-white font-bold py-3 px-8 rounded-lg shadow-lg" :disabled="isSubmittingUser">
                <span v-if="!isSubmittingUser">Personeli Kaydet</span>
                <span v-else class="animate-pulse">Kaydediliyor...</span>
              </button>
            </div>
          </form>

          <!-- Users List -->
          <div class="mt-12 border-t border-dark-border pt-8">
            <h3 class="text-lg font-bold text-white mb-4">Sistem Kullanıcıları</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-for="u in users" :key="u.id" class="p-4 bg-dark-bg border border-dark-border rounded-lg flex justify-between items-center hover:border-red-500/30 transition-colors group">
                <div>
                  <p class="text-white font-medium">{{ u.full_name }}</p>
                  <p class="text-xs text-gray-400 mt-1 uppercase">{{ u.role }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <div v-if="u.is_active" class="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.8)] mr-2"></div>
                  
                  <!-- Komisyon Ata ve Düzenle Tek Butonda Birleşti -->
                  <button @click="openEditUserModal(u)" class="px-4 py-1.5 bg-blue-500/10 text-blue-400 border border-blue-500/30 rounded hover:bg-blue-500 hover:text-white transition-colors text-xs font-bold flex items-center gap-2" title="Düzenle">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                    Düzenle
                  </button>

                  <button @click="deleteUser(u.id)" class="p-1.5 text-red-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors ml-2" title="Sil">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Activities Form -->
        <div v-show="activeTab === 'activities'" class="max-w-2xl">
           <div class="mb-8 border-b border-dark-border pb-4">
            <h2 class="text-xl font-bold text-white flex items-center gap-3">
               <svg class="w-6 h-6 text-neon-turquoise" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
               Yeni Aktivite Ekle
            </h2>
            <p class="text-xs text-gray-400 mt-1">Su sporları kataloğunuza yeni bir hizmet ekleyin.</p>
          </div>

          <form @submit.prevent="submitActivity" class="space-y-6">
            <div>
              <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Aktivite Adı *</label>
              <input v-model="activityForm.name" type="text" required class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" placeholder="Örn: Scuba Diving" />
            </div>

            <div class="flex items-center gap-3 p-4 bg-dark-bg rounded-lg border border-dark-border">
              <input v-model="activityForm.is_percentage_eligible" type="checkbox" id="pct" class="w-5 h-5 accent-neon-turquoise rounded bg-dark-surface border-dark-border" />
              <label for="pct" class="text-sm text-gray-300 select-none cursor-pointer">Yüzde Dağılımına Uygun (İnfocu komisyon alabilir)</label>
            </div>

            <div class="pt-4 flex justify-end">
              <button type="submit" class="bg-gradient-to-r from-neon-turquoise to-ocean-500 hover:from-neon-turquoise hover:to-ocean-400 text-white font-bold py-3 px-8 rounded-lg shadow-lg text-gray-900" :disabled="isSubmittingActivity">
                <span v-if="!isSubmittingActivity">Aktiviteyi Kaydet</span>
                <span v-else class="animate-pulse">Kaydediliyor...</span>
              </button>
            </div>
          </form>

          <!-- Activities List -->
          <div class="mt-12 border-t border-dark-border pt-8">
            <h3 class="text-lg font-bold text-white mb-4">Tanımlı Aktiviteler</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div v-for="a in activities" :key="a.id" class="p-4 bg-dark-bg border border-dark-border rounded-lg flex justify-between items-start hover:border-blue-500/30 transition-colors group">
                <div>
                  <p class="text-white font-medium">{{ a.name }}</p>
                  <p class="text-xs text-gray-400 mt-1" v-if="a.is_percentage_eligible">Komisyon: <span class="text-neon-turquoise">Aktif</span></p>
                </div>
                <button @click="openEditActivityModal(a)" class="p-1.5 text-blue-400 hover:text-blue-300 hover:bg-blue-400/10 rounded transition-colors opacity-0 group-hover:opacity-100" title="Düzenle">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- User Düzenleme Modalı (Parkur Takip UX Birebir) -->
    <div v-if="showEditUserModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4 py-8 overflow-y-auto">
      <div class="bg-dark-surface border border-dark-border rounded-xl shadow-2xl w-full max-w-2xl my-auto">
        <div class="p-6 border-b border-dark-border flex justify-between items-center bg-dark-bg">
          <h3 class="text-xl font-bold text-white">{{ editUserForm.full_name }} — Düzenle</h3>
          <button @click="closeEditUserModal" class="text-gray-400 hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        
        <div class="p-6 space-y-6">
          <div v-if="isLoadingRules" class="flex justify-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-neon-turquoise"></div>
          </div>
          <div v-else>
            <!-- Temel Bilgiler -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div>
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Ad Soyad</label>
                <input v-model="editUserForm.full_name" type="text" class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" />
              </div>
              <div v-if="selectedUser.role === 'infocu'">
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Hedef Ciro</label>
                <input v-model="editUserForm.target_revenue" type="number" step="0.01" class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" />
              </div>
              <div :class="selectedUser.role === 'infocu' ? 'md:col-span-2' : ''">
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Yeni Şifre (İsteğe Bağlı)</label>
                <input v-model="editUserForm.password" type="text" class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" placeholder="Değiştirmek istemiyorsanız boş bırakın" />
              </div>
            </div>

            <!-- Komisyon ve Aktiviteler (Artık Tüm Roller İçin Açık) -->
            <div class="bg-dark-bg rounded-xl border border-dark-border p-6 relative overflow-hidden">
              <div class="absolute top-0 left-0 w-1 h-full bg-neon-turquoise"></div>
              
              <div class="mb-6">
                <label class="block text-sm font-bold text-white mb-2">Yüzde % (Tüm Seçili Aktiviteler İçin)</label>
                <input v-model.number="globalPercentage" type="number" step="0.1" class="w-32 bg-dark-surface border border-neon-turquoise/50 rounded-lg px-4 py-2 text-xl font-bold text-neon-turquoise focus:outline-none focus:border-neon-turquoise transition-all" />
              </div>

              <div>
                <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Aktiviteler (Hangi aktivitelerden pay alacak?)</label>
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 max-h-64 overflow-y-auto pr-2 custom-scrollbar">
                  <div v-for="act in percentageEligibleActivities" :key="act.id" class="flex items-center gap-3">
                    <input 
                      type="checkbox" 
                      :id="'act_' + act.id"
                      :value="act.id"
                      v-model="selectedActivitiesForCommission"
                      class="w-5 h-5 accent-neon-turquoise rounded bg-dark-surface border-dark-border cursor-pointer" 
                    />
                    <label :for="'act_' + act.id" class="text-sm text-gray-300 cursor-pointer select-none">{{ act.name }}</label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-8 flex justify-end gap-3 border-t border-dark-border pt-6">
            <button @click="closeEditUserModal" class="px-6 py-2 text-gray-400 hover:text-white transition-colors bg-dark-bg border border-dark-border rounded-lg font-medium">İptal</button>
            <button @click="saveUserEdits" class="px-8 py-2 bg-gradient-to-r from-ocean-600 to-neon-turquoise hover:from-ocean-500 hover:to-neon-turquoise text-white font-bold rounded-lg shadow-lg transition-all" :disabled="isSavingEdits || isLoadingRules">
              <span v-if="!isSavingEdits">Kaydet</span>
              <span v-else>Kaydediliyor...</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Düzenleme Modalı -->
    <div v-if="showEditActivityModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div class="bg-dark-surface border border-dark-border rounded-xl shadow-2xl w-full max-w-md my-auto">
        <div class="p-6 border-b border-dark-border flex justify-between items-center bg-dark-bg">
          <h3 class="text-xl font-bold text-white">Aktivite Düzenle</h3>
          <button @click="closeEditActivityModal" class="text-gray-400 hover:text-white transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
        
        <div class="p-6 space-y-6">
          <div>
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Aktivite Adı</label>
            <input v-model="editActivityForm.name" type="text" class="w-full bg-dark-bg border border-dark-border rounded-lg px-4 py-3 text-white focus:outline-none focus:border-neon-turquoise transition-all" />
          </div>

          <div class="flex items-center gap-3 p-4 bg-dark-bg rounded-lg border border-dark-border">
            <input v-model="editActivityForm.is_percentage_eligible" type="checkbox" id="edit_pct" class="w-5 h-5 accent-neon-turquoise rounded bg-dark-surface border-dark-border" />
            <label for="edit_pct" class="text-sm text-gray-300 select-none cursor-pointer">Yüzde Dağılımına Uygun</label>
          </div>

          <div class="mt-8 flex justify-end gap-3 pt-4 border-t border-dark-border">
            <button @click="closeEditActivityModal" class="px-6 py-2 text-gray-400 hover:text-white transition-colors bg-dark-bg border border-dark-border rounded-lg font-medium">İptal</button>
            <button @click="saveActivityEdits" class="px-8 py-2 bg-neon-turquoise hover:bg-turquoise-400 text-dark-bg font-bold rounded-lg shadow-lg transition-all" :disabled="isSavingActivityEdits">
              <span v-if="!isSavingActivityEdits">Kaydet</span>
              <span v-else>Kaydediliyor...</span>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '@/utils/axios'
import { useToast } from 'vue-toastification'

const toast = useToast()
const activeTab = ref('users')

const users = ref([])
const activities = ref([])

// Edit User / Commission Modal State
const showEditUserModal = ref(false)
const selectedUser = ref(null)
const isSavingEdits = ref(false)
const isLoadingRules = ref(false)

const editUserForm = reactive({
  full_name: '',
  target_revenue: '',
  password: ''
})

const globalPercentage = ref(0)
const selectedActivitiesForCommission = ref([])

const percentageEligibleActivities = computed(() => {
  return activities.value.filter(a => a.is_percentage_eligible)
})

// Activity Edit Modal State
const showEditActivityModal = ref(false)
const selectedActivity = ref(null)
const isSavingActivityEdits = ref(false)
const editActivityForm = reactive({
  name: '',
  is_percentage_eligible: true
})

// User State
const isSubmittingUser = ref(false)
const userForm = reactive({
  full_name: '',
  role: '',
  password: '',
  target_revenue: ''
})

const submitUser = async () => {
  isSubmittingUser.value = true
  try {
    const payload = { ...userForm }
    if (!payload.target_revenue) delete payload.target_revenue
    else payload.target_revenue = parseFloat(payload.target_revenue)

    await api.post('/users/', payload)
    toast.success('Personel başarıyla oluşturuldu!')
    
    userForm.full_name = ''
    userForm.role = ''
    userForm.password = ''
    userForm.target_revenue = ''
    
    fetchUsers()
  } catch (error) {
    console.error(error)
  } finally {
    isSubmittingUser.value = false
  }
}

// Activity State
const isSubmittingActivity = ref(false)
const activityForm = reactive({
  name: '',
  is_percentage_eligible: true
})

const submitActivity = async () => {
  isSubmittingActivity.value = true
  try {
    await api.post('/activities/', { ...activityForm })
    toast.success('Aktivite sisteme eklendi!')
    
    activityForm.name = ''
    activityForm.is_percentage_eligible = true
    
    fetchActivities()
  } catch (error) {
    console.error(error)
  } finally {
    isSubmittingActivity.value = false
  }
}

const fetchUsers = async () => {
  try {
    const res = await api.get('/users/')
    users.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const fetchActivities = async () => {
  try {
    const res = await api.get('/activities/')
    activities.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const deleteUser = async (userId) => {
  if(!confirm('Bu kullanıcıyı silmek (pasife almak) istediğinize emin misiniz?')) return
  try {
    await api.delete(`/users/${userId}`)
    toast.success('Kullanıcı başarıyla silindi.')
    fetchUsers()
  } catch(e) {
    console.error(e)
    toast.error('Silme işlemi başarısız oldu.')
  }
}

const openEditUserModal = async (user) => {
  selectedUser.value = user
  editUserForm.full_name = user.full_name
  editUserForm.target_revenue = user.target_revenue || ''
  editUserForm.password = ''
  
  globalPercentage.value = 0
  selectedActivitiesForCommission.value = []
  
  // Bütün rollere açtığımız için rol kontrolünü kaldırdık
  isLoadingRules.value = true
  showEditUserModal.value = true
  try {
    const res = await api.get(`/users/${user.id}/percentage-rules/`)
    const rules = res.data || []
    
    if (rules.length > 0) {
      globalPercentage.value = parseFloat(rules[0].percentage_rate)
      selectedActivitiesForCommission.value = rules.map(r => r.activity_id)
    }
  } catch (e) {
    console.error(e)
    // Sadece konsola yaz, tost göstermeye gerek yok (yeni kullanıcıda kural olmayabilir)
  } finally {
    isLoadingRules.value = false
  }
}

const closeEditUserModal = () => {
  showEditUserModal.value = false
  selectedUser.value = null
}

const saveUserEdits = async () => {
  if (!selectedUser.value) return
  isSavingEdits.value = true
  
  try {
    const putPayload = {
      full_name: editUserForm.full_name
    }
    if (editUserForm.password && editUserForm.password.trim() !== '') {
      putPayload.password = editUserForm.password
    }
    if (selectedUser.value.role === 'infocu') {
      putPayload.target_revenue = editUserForm.target_revenue ? parseFloat(editUserForm.target_revenue) : null
    }
    
    await api.put(`/users/${selectedUser.value.id}`, putPayload)
    
    // 2. Komisyonları Güncelle (Artık tüm roller için aktif)
    if (selectedActivitiesForCommission.value.length > 0 && globalPercentage.value <= 0) {
      toast.warning('Seçili aktiviteler var fakat yüzde girilmedi. Komisyonlar atanmayabilir.')
    } else {
      const rulesPayload = selectedActivitiesForCommission.value.map(actId => ({
        activity_id: actId,
        percentage_rate: globalPercentage.value
      }))
      
      // POST API zaten öncekileri silip yenileri ekliyor
      await api.post(`/users/${selectedUser.value.id}/percentage-rules/`, rulesPayload)
    }

    toast.success('Kullanıcı güncellendi!')
    fetchUsers()
    closeEditUserModal()
  } catch (error) {
    console.error(error)
    toast.error('Güncellenirken bir hata oluştu.')
  } finally {
    isSavingEdits.value = false
  }
}

// Activity Modal Logic
const openEditActivityModal = (activity) => {
  selectedActivity.value = activity
  editActivityForm.name = activity.name
  editActivityForm.is_percentage_eligible = activity.is_percentage_eligible
  showEditActivityModal.value = true
}

const closeEditActivityModal = () => {
  showEditActivityModal.value = false
  selectedActivity.value = null
}

const saveActivityEdits = async () => {
  if (!selectedActivity.value) return
  isSavingActivityEdits.value = true
  
  try {
    await api.put(`/activities/${selectedActivity.value.id}`, { ...editActivityForm })
    toast.success('Aktivite güncellendi!')
    fetchActivities()
    closeEditActivityModal()
  } catch (error) {
    console.error(error)
    toast.error('Aktivite güncellenirken hata oluştu.')
  } finally {
    isSavingActivityEdits.value = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchActivities()
})
</script>
