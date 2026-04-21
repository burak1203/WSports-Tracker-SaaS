import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/subscription-expired',
    name: 'SubscriptionExpired',
    component: () => import('@/views/SubscriptionExpired.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { roles: ['admin', 'kasa', 'yuzdeci'] }
      },
      {
        path: 'sales',
        name: 'SalesPanel',
        component: () => import('@/views/SalesPanel.vue'),
        meta: { roles: ['admin', 'kasa', 'infocu'] }
      },
      {
        path: 'expenses',
        name: 'Expenses',
        component: () => import('@/views/Expenses.vue'),
        meta: { roles: ['admin', 'kasa'] }
      },
      {
        path: 'personnel-activity',
        name: 'PersonnelActivity',
        component: () => import('@/views/PersonnelActivity.vue'),
        meta: { roles: ['admin'] }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/Reports.vue'),
        meta: { roles: ['admin', 'yuzdeci'] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = !!authStore.token

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.meta.guest && isAuthenticated) {
    if (authStore.user?.role === 'infocu') {
      next({ name: 'SalesPanel' })
    } else {
      next({ name: 'Dashboard' })
    }
  } else if (to.meta.roles && authStore.user) {
    if (to.meta.roles.includes(authStore.user.role)) {
      next()
    } else {
      if (authStore.user.role === 'infocu') {
        next({ name: 'SalesPanel' })
      } else {
        next({ name: 'Dashboard' })
      }
    }
  } else {
    if (to.path === '/' && authStore.user) {
        if (authStore.user.role === 'infocu') next({ name: 'SalesPanel' })
        else next({ name: 'Dashboard' })
    } else {
        next()
    }
  }
})

export default router
