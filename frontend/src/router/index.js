import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import MainLayout from '../layouts/MainLayout.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/LoginView.vue'),
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        component: MainLayout,
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                name: 'Dashboard',
                component: () => import('../views/DashboardView.vue')
            },
            {
                path: 'sales',
                name: 'Sales',
                component: () => import('../views/SalesView.vue')
            },
            {
                path: 'system',
                name: 'System',
                component: () => import('../views/SystemView.vue'),
                meta: { roles: ['admin'] } // Sadece admin girebilir
            }
        ]
    },
    {
        path: '/:pathMatch(.*)*',
        redirect: '/'
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Navigation Guard (Güvenlik Duvarı)
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()
    const isAuthenticated = !!authStore.token

    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login')
    } else if (to.name === 'Login' && isAuthenticated) {
        next('/')
    } else if (to.meta.roles && !to.meta.roles.includes(authStore.user?.role)) {
        // Yetkisi olmayan bir yere girmeye çalışıyorsa anasayfaya at
        next('/')
    } else {
        next()
    }
})

export default router