<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
    
    <div class="space-y-6">
      <div class="bg-slate-50 p-5 rounded-xl border border-slate-200">
        <h2 class="text-lg font-bold text-slate-800 mb-4 border-b pb-2">Yeni Aktivite Ekle</h2>
        <form @submit.prevent="createActivity" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Aktivite Adı</label>
            <input v-model="activityForm.name" type="text" required class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none" placeholder="Örn: Parasailing">
          </div>
          <div class="flex items-center gap-2">
            <input v-model="activityForm.is_percentage_eligible" type="checkbox" id="eligible" class="w-4 h-4 text-blue-600 rounded border-gray-300">
            <label for="eligible" class="text-sm font-medium text-slate-700">Bu aktiviteden komisyon (yüzde) verilebilir.</label>
          </div>
          <button type="submit" :disabled="isSubmittingActivity" class="w-full bg-slate-800 text-white font-bold py-2.5 rounded hover:bg-slate-700 transition-colors disabled:opacity-50">
            Aktiviteyi Kaydet
          </button>
        </form>
      </div>

      <div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div class="p-4 bg-slate-50 border-b flex justify-between items-center">
          <h3 class="font-bold text-slate-800">Tüm Su Sporları</h3>
          <button @click="fetchActivities" class="text-xs text-blue-600 hover:text-blue-800 font-semibold">Yenile</button>
        </div>
        <table class="w-full text-left border-collapse">
          <tbody>
            <tr v-if="activities.length === 0">
              <td colspan="2" class="p-4 text-center text-gray-500 text-sm">Kayıtlı aktivite yok.</td>
            </tr>
            <tr v-for="act in activities" :key="act.id" :class="act.is_active ? 'hover:bg-slate-50' : 'bg-gray-100 opacity-75'" class="border-b last:border-0 transition-colors">
              <td class="p-3">
                <p class="font-semibold text-slate-800">{{ act.name }} <span v-if="!act.is_active" class="text-xs text-red-500 ml-2">(Pasif)</span></p>
                <div class="flex items-center gap-2 mt-1">
                  <label class="inline-flex items-center cursor-pointer">
                    <input type="checkbox" :checked="act.is_percentage_eligible" @change="toggleEligible(act)" class="sr-only peer">
                    <div class="relative w-7 h-4 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-blue-600"></div>
                    <span class="ms-2 text-xs font-medium" :class="act.is_percentage_eligible ? 'text-blue-600' : 'text-gray-500'">Komisyon</span>
                  </label>
                </div>
              </td>
              <td class="p-3 text-right">
                <button @click="toggleActivityStatus(act)" class="text-xs font-semibold px-2 py-1 rounded" :class="act.is_active ? 'bg-red-50 text-red-600' : 'bg-green-100 text-green-700'">
                  {{ act.is_active ? 'Pasife Çek' : 'Aktifleştir' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="bg-blue-50/50 p-5 rounded-xl border border-blue-100 h-fit">
      <h2 class="text-lg font-bold text-blue-900 mb-4 border-b border-blue-200 pb-2">Personel Komisyon Oranları</h2>
      <div class="mb-6">
        <label class="block text-sm font-medium text-slate-700 mb-1">Personel Seçin</label>
        <select v-model="selectedUserId" @change="loadUserRules" class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 outline-none bg-white">
          <option :value="null">-- Bir personel seçin --</option>
          <option v-for="user in eligibleUsers" :key="user.id" :value="user.id">
            {{ user.full_name }} ({{ user.role.toUpperCase() }})
          </option>
        </select>
      </div>

      <div v-if="selectedUserId">
        <div v-if="eligibleActivities.length === 0" class="text-sm text-orange-600 bg-orange-50 p-3 rounded border border-orange-100">
          Sistemde komisyona açık aktif hiçbir aktivite bulunmuyor.
        </div>
        <form v-else @submit.prevent="saveRules" class="space-y-3">
          <div v-for="act in eligibleActivities" :key="act.id" class="flex items-center justify-between bg-white p-3 rounded border border-gray-200 shadow-sm">
            <span class="text-sm font-semibold text-slate-700">{{ act.name }}</span>
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-gray-400">%</span>
              <input v-model="ruleForm[act.id]" type="number" step="0.01" min="0" max="100" class="w-20 p-1.5 text-right border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 text-sm font-bold">
            </div>
          </div>
          <button type="submit" :disabled="isSavingRules" class="w-full mt-4 bg-blue-600 text-white font-bold py-2.5 rounded hover:bg-blue-700 disabled:opacity-50">
            {{ isSavingRules ? 'Kaydediliyor...' : 'Oranları Güncelle' }}
          </button>
        </form>
      </div>
      <div v-else class="text-center py-10 text-gray-400 text-sm border-2 border-dashed border-gray-200 rounded-lg">
        Yukarıdan bir personel seçin.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from '@/utils/axios'

const activities = ref([])
const isSubmittingActivity = ref(false)
const activityForm = ref({ name: '', is_percentage_eligible: true })

const users = ref([])
const selectedUserId = ref(null)
const ruleForm = ref({})
const isSavingRules = ref(false)

const eligibleUsers = computed(() => users.value.filter(u => u.role === 'infocu' || u.role === 'yuzdeci'))
const eligibleActivities = computed(() => activities.value.filter(a => a.is_percentage_eligible && a.is_active))

// YENİ: include_inactive=true parametresi eklendi
const fetchActivities = async () => {
  try {
    const res = await axios.get('/activities/?include_inactive=true')
    activities.value = res.data
  } catch (err) {
    console.error("Aktiviteler çekilemedi", err)
  }
}

const fetchUsers = async () => {
  try {
    const res = await axios.get('/users/')
    users.value = res.data
  } catch (err) {
    console.error("Kullanıcılar çekilemedi", err)
  }
}

const createActivity = async () => {
  isSubmittingActivity.value = true
  try {
    await axios.post('/activities/', activityForm.value)
    activityForm.value.name = ''
    activityForm.value.is_percentage_eligible = true
    await fetchActivities()
  } catch (err) {
    alert(err.response?.data?.detail || "Aktivite eklenemedi.")
  } finally {
    isSubmittingActivity.value = false
  }
}

const toggleActivityStatus = async (act) => {
  try {
    await axios.put(`/activities/${act.id}`, { is_active: !act.is_active })
    await fetchActivities()
  } catch (err) {
    alert("Durum güncellenemedi.")
  }
}

// YENİ: Komisyon Uygunluğunu Değiştiren Fonksiyon
const toggleEligible = async (act) => {
  try {
    await axios.put(`/activities/${act.id}`, { is_percentage_eligible: !act.is_percentage_eligible })
    await fetchActivities()
  } catch (err) {
    alert("Komisyon durumu güncellenemedi.")
  }
}

const loadUserRules = async () => {
  if (!selectedUserId.value) return
  ruleForm.value = {}
  try {
    const res = await axios.get(`/users/${selectedUserId.value}/percentage-rules/`)
    res.data.forEach(rule => { ruleForm.value[rule.activity_id] = rule.percentage_rate })
  } catch (err) {
    console.error("Kurallar çekilemedi", err)
  }
}

const saveRules = async () => {
  if (!selectedUserId.value) return
  isSavingRules.value = true
  const payload = Object.entries(ruleForm.value)
    .filter(([_, rate]) => rate !== null && rate !== '')
    .map(([actId, rate]) => ({ activity_id: parseInt(actId), percentage_rate: parseFloat(rate) }))

  try {
    await axios.post(`/users/${selectedUserId.value}/percentage-rules/`, payload)
    alert("Komisyon oranları başarıyla güncellendi.")
  } catch (err) {
    alert("Kurallar kaydedilemedi.")
  } finally {
    isSavingRules.value = false
  }
}

onMounted(async () => {
  await fetchActivities()
  await fetchUsers()
})
</script>