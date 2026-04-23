import { defineStore } from 'pinia'
import api from '@/utils/axios'

export const useCoreStore = defineStore('core', {
    state: () => ({
        exchangeRates: {
            eur: 1, // Fallback değerler (API çökerse diye)
            usd: 1,
            gbp: 1
        },
        activities: [],
        infocus: [], // Aktif infocular
        yuzdelikciler: [], // Aktif yüzdelikçiler
        isLoaded: false
    }),
    actions: {
        async fetchInitialData() {
            try {
                // 1. Backend'den veya Harici API'den kurları çek (Şimdilik mock veya backend uç noktasından)
                // TODO: Backend'e bir GET /exchange-rates ucu yazılmalı veya harici API kullanılmalı.
                // Şimdilik test için statik değerler atıyoruz.
                this.exchangeRates = { eur: 35.0, usd: 32.5, gbp: 40.0 }

                // 2. Aktiviteleri Çek
                const resActivities = await api.get('/activities/')
                this.activities = resActivities.data

                // 3. Kullanıcıları çekip rolüne göre belleğe ayır
                const resUsers = await api.get('/users/')
                if (Array.isArray(resUsers.data)) {
                    this.infocus = resUsers.data.filter(u => u.role === 'infocu' && u.is_active)
                    this.yuzdelikciler = resUsers.data.filter(u => u.role === 'yuzdeci' && u.is_active)
                }

                this.isLoaded = true
            } catch (error) {
                console.error("Core verileri yüklenirken hata oluştu:", error)
            }
        }
    }
})