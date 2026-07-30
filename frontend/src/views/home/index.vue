<template>
  <div class="home">
    <!-- 1. 品牌渐变 Hero -->
    <el-card class="hero" shadow="never">
      <div class="hero-glow glow-a" />
      <div class="hero-glow glow-b" />
      <div class="hero-inner">
        <div class="hero-left">
          <span class="hero-pill">工作台</span>
          <h1 class="hero-title">IT 综合运维管理系统</h1>
          <p class="hero-welcome">
            欢迎回来，<b>{{ displayName }}</b>
            <span class="hero-dot">·</span>
            <span>{{ today }}</span>
          </p>
          <div class="hero-chips">
            <span
              v-for="c in quickChips"
              :key="c.to"
              class="hero-chip"
              @click="go(c.to)"
            >
              <el-icon :size="15"><component :is="c.icon" /></el-icon>
              {{ c.label }}
            </span>
          </div>
        </div>
        <div class="hero-orb">
          <el-icon :size="64"><DataAnalysis /></el-icon>
          <span class="orb-ring" />
        </div>
      </div>
    </el-card>

    <!-- 2. 业务数据概览 KPI 行 -->
    <div class="kpi-grid">
      <el-card
        v-for="k in kpis"
        :key="k.key"
        class="kpi-card"
        shadow="hover"
        @click="go(k.to)"
      >
        <div class="kpi-icon" :style="{ background: k.color }">
          <el-icon :size="24"><component :is="k.icon" /></el-icon>
        </div>
        <div class="kpi-body">
          <div class="kpi-num">{{ k.count }}</div>
          <div class="kpi-label">{{ k.label }}</div>
        </div>
        <el-icon class="kpi-arrow" :size="16"><ArrowRight /></el-icon>
      </el-card>
    </div>

    <!-- 3. 模块导航卡片 -->
    <div class="module-section">
      <div class="module-grid">
        <el-card
          v-for="m in modules"
          :key="m.title"
          class="module-card"
          shadow="hover"
          @click="go(m.to)"
        >
          <span class="module-bar" :style="{ background: m.color }" />
          <div class="module-icon" :style="{ background: m.color }">
            <el-icon :size="26"><component :is="m.icon" /></el-icon>
          </div>
          <div class="module-title">{{ m.title }}</div>
          <div class="module-desc">{{ m.desc }}</div>
          <div class="module-links">
            <span
              v-for="sub in m.subs"
              :key="sub.to"
              class="module-link"
              @click.stop="go(sub.to)"
            >{{ sub.label }}</span>
          </div>
          <el-icon class="module-arrow" :size="16"><ArrowRight /></el-icon>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserStore } from '@/stores/user'
import {
  Monitor, Share, Lock, Setting,
  DataAnalysis, Connection, Tickets, Key, Position, ArrowRight,
} from '@element-plus/icons-vue'
import { getAssets } from '@/api/asset'
import { getPortConnections } from '@/api/port-connection'
import { getExternalBroadbands } from '@/api/external-broadband'
import { getIPPlans } from '@/api/ip-plan'
import { getIPAllocations } from '@/api/ip-allocation'

const router = useRouter()
const userStore = useUserStore()
const { isAdmin, username, realName } = storeToRefs(userStore)

const today = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
})
const displayName = computed(() => realName.value || username.value || '用户')

const quickChips = computed(() => {
  const base = [
    { label: '资产统计', icon: DataAnalysis, to: '/asset/statistics' },
    { label: '端口互联', icon: Connection, to: '/asset/port-connection' },
    { label: 'IP分配', icon: Tickets, to: '/ip/ip-allocation' },
  ]
  if (isAdmin.value) base.push({ label: '授权', icon: Key, to: '/asset/license' })
  return base
})

const kpis = reactive([
  { key: 'asset', label: '资产总数', icon: DataAnalysis, color: 'linear-gradient(135deg,#409EFF,#66b1ff)', to: '/asset/statistics', count: 0 },
  { key: 'port', label: '端口互联', icon: Connection, color: 'linear-gradient(135deg,#36cfc9,#5cdbd3)', to: '/asset/port-connection', count: 0 },
  { key: 'ips', label: 'IPS带宽', icon: Position, color: 'linear-gradient(135deg,#722ed1,#9254de)', to: '/asset/external-broadband', count: 0 },
  { key: 'plan', label: 'IP规划', icon: Share, color: 'linear-gradient(135deg,#52c41a,#73d13d)', to: '/ip/ip-plan', count: 0 },
  { key: 'alloc', label: 'IP分配', icon: Tickets, color: 'linear-gradient(135deg,#fa8c16,#ffa940)', to: '/ip/ip-allocation', count: 0 },
])

const modules = [
  {
    title: '资产管理', icon: Monitor,
    color: 'linear-gradient(135deg,#409EFF,#66b1ff)', to: '/asset/statistics',
    desc: '资产统计、端口互联、IPS带宽与授权',
    subs: [
      { label: '资产统计', to: '/asset/statistics' },
      { label: '端口互联', to: '/asset/port-connection' },
      { label: 'IPS带宽', to: '/asset/external-broadband' },
      { label: '授权管理', to: '/asset/license' },
    ],
  },
  {
    title: 'IP 管理', icon: Share,
    color: 'linear-gradient(135deg,#67C23A,#85ce61)', to: '/ip/ip-plan',
    desc: 'IP 规划、分配与互联',
    subs: [
      { label: 'IP地址规划', to: '/ip/ip-plan' },
      { label: 'IP地址分配表', to: '/ip/ip-allocation' },
      { label: '互联IP', to: '/ip/interconnect-ip' },
    ],
  },
  {
    title: '权限管理', icon: Lock,
    color: 'linear-gradient(135deg,#E6A23C,#ebb563)', to: '/permission',
    desc: '授权与访问控制',
    subs: [],
  },
  {
    title: '系统管理', icon: Setting,
    color: 'linear-gradient(135deg,#909399,#a6a9ad)', to: '/system/user',
    desc: '用户、角色、审计与表单设计',
    subs: [
      { label: '用户管理', to: '/system/user' },
      { label: '角色管理', to: '/system/role' },
      { label: '审计管理', to: '/system/audit' },
      { label: '表单设计', to: '/system/designer' },
    ],
  },
]

const fetchers = {
  asset: () => getAssets({ limit: 1, skip: 0 }),
  port: () => getPortConnections({ limit: 1, skip: 0 }),
  ips: () => getExternalBroadbands({ limit: 1, skip: 0 }),
  plan: () => getIPPlans({ limit: 1, skip: 0 }),
  alloc: () => getIPAllocations({ limit: 1, skip: 0 }),
}

async function loadCounts() {
  await Promise.all(kpis.map(async (k) => {
    try {
      const d = await fetchers[k.key]()
      k.count = d?.total ?? 0
    } catch {
      k.count = 0
    }
  }))
}

function go(to) {
  router.push(to)
}

onMounted(loadCounts)
</script>

<style scoped>
.home {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ---------- Hero ---------- */
.hero {
  position: relative;
  overflow: hidden;
  border: none;
  border-radius: 18px;
  background: linear-gradient(120deg, #2b6cff 0%, #1f8fff 48%, #12d3d3 100%);
  color: #fff;
}
.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.55;
  z-index: 1;
  pointer-events: none;
}
.glow-a {
  width: 320px; height: 320px;
  top: -140px; right: 120px;
  background: radial-gradient(circle, rgba(255,255,255,0.55), transparent 70%);
}
.glow-b {
  width: 260px; height: 260px;
  bottom: -130px; left: 8%;
  background: radial-gradient(circle, rgba(18,211,211,0.6), transparent 70%);
}
.hero-inner {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 30px 34px;
}
.hero-pill {
  display: inline-block;
  padding: 4px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(4px);
}
.hero-title {
  margin: 14px 0 8px;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: 0.5px;
}
.hero-welcome {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.92);
}
.hero-welcome b { font-weight: 700; }
.hero-dot { margin: 0 8px; opacity: 0.7; }
.hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}
.hero-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.28);
  transition: background 0.2s, transform 0.2s;
}
.hero-chip:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}
.hero-orb {
  position: relative;
  flex: 0 0 auto;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.18), inset 0 0 30px rgba(255, 255, 255, 0.15);
}
.orb-ring {
  position: absolute;
  inset: -10px;
  border-radius: 50%;
  border: 2px dashed rgba(255, 255, 255, 0.45);
  animation: orb-spin 14s linear infinite;
}
@keyframes orb-spin {
  to { transform: rotate(360deg); }
}

/* ---------- KPI ---------- */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 18px;
}
.kpi-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 16px;
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(31, 143, 255, 0.18);
}
.kpi-icon {
  width: 50px;
  height: 50px;
  flex: 0 0 auto;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.kpi-body { flex: 1; min-width: 0; }
.kpi-num {
  font-size: 28px;
  font-weight: 800;
  line-height: 1.1;
  color: var(--el-text-color-primary);
}
.kpi-label {
  margin-top: 2px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.kpi-arrow {
  color: var(--el-text-color-placeholder);
  opacity: 0;
  transform: translateX(-6px);
  transition: opacity 0.2s, transform 0.2s;
}
.kpi-card:hover .kpi-arrow {
  opacity: 1;
  transform: translateX(0);
  color: var(--el-color-primary);
}

/* ---------- Module cards ---------- */
.module-section {
  border-radius: 18px;
  padding: 22px;
  background:
    radial-gradient(120% 120% at 0% 0%, rgba(64, 158, 255, 0.06), transparent 60%),
    radial-gradient(120% 120% at 100% 100%, rgba(18, 211, 211, 0.06), transparent 60%);
}
.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}
.module-card {
  position: relative;
  cursor: pointer;
  border-radius: 16px;
  overflow: hidden;
  transition: transform 0.25s, box-shadow 0.25s;
}
.module-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 34px rgba(0, 0, 0, 0.14);
}
.module-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  opacity: 0;
  transition: opacity 0.25s;
}
.module-card:hover .module-bar { opacity: 1; }
.module-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 14px;
  transition: transform 0.3s ease;
}
.module-card:hover .module-icon {
  transform: scale(1.12) rotate(-6deg);
}
.module-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}
.module-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin: 6px 0 12px;
  min-height: 38px;
}
.module-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.module-link {
  font-size: 12px;
  padding: 3px 10px;
  background: var(--el-fill-color-light);
  border-radius: 20px;
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.module-link:hover {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}
.module-arrow {
  position: absolute;
  right: 16px;
  bottom: 16px;
  color: var(--el-color-primary);
  opacity: 0;
  transform: translateX(-6px);
  transition: opacity 0.25s, transform 0.25s;
}
.module-card:hover .module-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* ---------- Responsive ---------- */
@media (max-width: 1100px) {
  .kpi-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 680px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .hero-inner { flex-direction: column; align-items: flex-start; }
  .hero-orb { display: none; }
}
</style>
