import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/asset',
    children: [
      {
        path: 'asset',
        name: 'Asset',
        component: () => import('@/views/asset/index.vue'),
        meta: { title: '资产管理', icon: 'Monitor' },
      },
      {
        path: 'permission',
        name: 'Permission',
        component: () => import('@/views/permission/index.vue'),
        meta: { title: '权限管理', icon: 'Key' },
      },
      {
        path: 'user',
        name: 'User',
        component: () => import('@/views/user/index.vue'),
        meta: { title: '用户管理', icon: 'User', adminOnly: true },
      },
      {
        path: 'role',
        name: 'Role',
        component: () => import('@/views/role/index.vue'),
        meta: { title: '角色管理', icon: 'UserFilled', adminOnly: true },
      },
      {
        path: 'audit',
        name: 'Audit',
        component: () => import('@/views/audit/index.vue'),
        meta: { title: '审计日志', icon: 'Document', adminOnly: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, from, next) => {
  document.title = to.meta.title
    ? `${to.meta.title} - IT运维管理系统`
    : 'IT 综合运维管理系统'

  const userStore = useUserStore()

  if (to.meta.public) {
    // Public route (login page)
    if (userStore.isLoggedIn) {
      next('/')
    } else {
      next()
    }
  } else {
    // Protected route
    if (!userStore.isLoggedIn) {
      next('/login')
    } else if (to.meta.adminOnly && !userStore.isAdmin) {
      next('/')
    } else {
      next()
    }
  }
})

export default router
