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
    redirect: '/home',
    children: [
      // 首页（图标化入口，无子级）
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/home/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled' },
      },
      // 资产管理
      {
        path: 'asset',
        redirect: '/asset/statistics',
        meta: { title: '资产管理', icon: 'Monitor' },
        children: [
          {
            path: 'statistics',
            name: 'AssetStatistics',
            component: () => import('@/views/asset/statistics/index.vue'),
            meta: { title: '资产统计', icon: 'DataAnalysis' },
          },
          {
            path: 'port-connection',
            name: 'PortConnection',
            component: () => import('@/views/asset/port-connection/index.vue'),
            meta: { title: '端口互联', icon: 'Connection' },
          },
          {
            path: 'external-broadband',
            name: 'ExternalBroadband',
            component: () => import('@/views/asset/external-broadband/index.vue'),
            meta: { title: 'IPS带宽', icon: 'Position' },
          },
          {
            path: 'license',
            name: 'License',
            component: () => import('@/views/asset/license/index.vue'),
            meta: { title: '授权管理', icon: 'Key' },
          },
        ],
      },
      // IP 管理
      {
        path: 'ip',
        redirect: '/ip/ip-plan',
        meta: { title: 'IP管理', icon: 'Share' },
        children: [
          {
            path: 'ip-plan',
            name: 'IPPlan',
            component: () => import('@/views/ip/ip-plan/index.vue'),
            meta: { title: 'IP地址规划', icon: 'Grid' },
          },
          {
            path: 'ip-allocation',
            name: 'IPAllocation',
            component: () => import('@/views/ip/ip-allocation/index.vue'),
            meta: { title: 'IP地址分配表', icon: 'Tickets' },
          },
          {
            path: 'interconnect-ip',
            name: 'InterconnectIP',
            component: () => import('@/views/ip/interconnect-ip/index.vue'),
            meta: { title: '互联IP', icon: 'Connection' },
          },
        ],
      },
      // 权限管理（一级菜单，骨架页）
      {
        path: 'permission',
        name: 'Permission',
        component: () => import('@/views/permission/index.vue'),
        meta: { title: '权限管理', icon: 'Lock' },
      },
      // 系统管理
      {
        path: 'system',
        redirect: '/system/user',
        meta: { title: '系统管理', icon: 'Setting' },
        children: [
          {
            path: 'user',
            name: 'User',
            component: () => import('@/views/system/user/index.vue'),
            meta: { title: '用户管理', icon: 'User', adminOnly: true },
          },
          {
            path: 'role',
            name: 'Role',
            component: () => import('@/views/system/role/index.vue'),
            meta: { title: '角色管理', icon: 'UserFilled', adminOnly: true },
          },
          {
            path: 'audit',
            name: 'Audit',
            component: () => import('@/views/system/audit/index.vue'),
            meta: { title: '审计管理', icon: 'Memo', adminOnly: true },
          },
          {
            path: 'designer',
            name: 'Designer',
            component: () => import('@/views/system/designer/index.vue'),
            meta: { title: '表单设计', icon: 'EditPen', adminOnly: true },
          },
        ],
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
