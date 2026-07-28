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
        component: () => import('@/layouts/AssetLayout.vue'),
        redirect: '/asset/statistics',
        meta: { title: '资产管理', icon: 'Monitor' },
        children: [
          {
            path: 'statistics',
            name: 'AssetStatistics',
            component: () => import('@/views/asset/index.vue'),
            meta: { title: '资产统计', icon: 'DataAnalysis' },
          },
          {
            path: 'port-connection',
            name: 'PortConnection',
            component: () => import('@/views/asset/port-connection.vue'),
            meta: { title: '端口互联', icon: 'Connection' },
          },
          {
            path: 'ip-plan',
            name: 'IPPlan',
            component: () => import('@/views/asset/ip-plan.vue'),
            meta: { title: 'IP地址规划', icon: 'Grid' },
          },
          {
            path: 'interconnect-ip',
            name: 'InterconnectIP',
            component: () => import('@/views/asset/interconnect-ip.vue'),
            meta: { title: '互联IP', icon: 'Share' },
          },
          {
            path: 'external-broadband',
            name: 'ExternalBroadband',
            component: () => import('@/views/asset/external-broadband.vue'),
            meta: { title: '外线宽带', icon: 'Position' },
          },
          {
            path: 'license',
            name: 'License',
            component: () => import('@/views/asset/license.vue'),
            meta: { title: '授权管理', icon: 'Key' },
          },
        ],
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
      {
        path: 'designer',
        name: 'Designer',
        component: () => import('@/views/designer/index.vue'),
        meta: { title: '表单设计', icon: 'EditPen', adminOnly: true },
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
