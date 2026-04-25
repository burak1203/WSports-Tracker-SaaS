import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
    state: () => {
        let savedUser = null;
        try {
            const userStr = localStorage.getItem('user');
            if (userStr && userStr !== 'undefined') {
                savedUser = JSON.parse(userStr);
            }
        } catch (e) {
            console.error('Failed to parse user from localStorage', e);
        }

        return {
            // Sayfa yenilendiğinde token kaybolmasın diye localStorage'dan okuyoruz
            token: localStorage.getItem('token') || null,
            user: savedUser
        }
    },
    actions: {
        setAuth(token, user) {
            this.token = token
            this.user = user || null
            localStorage.setItem('token', token)
            if (user) {
                localStorage.setItem('user', JSON.stringify(user))
            } else {
                localStorage.removeItem('user')
            }
        },
        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            localStorage.removeItem('user')
        }
    }
})