<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <el-icon size="28" color="#409EFF"><Setting /></el-icon>
        <span v-show="!appStore.sidebarCollapsed" class="logo-text">IT运维系统</span>
      </div>
      <el-menu
        :default-active="route.path"
        :default-openeds="['/asset', '/ip', '/system']"
        :collapse="appStore.sidebarCollapsed"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        class="sidebar-menu"
      >
        <!-- 首页（图标化入口，无子级） -->
        <el-menu-item index="/home">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <!-- 资产管理 -->
        <el-sub-menu index="/asset">
          <template #title>
            <el-icon><Monitor /></el-icon>
            <span>资产管理</span>
          </template>
          <el-menu-item index="/asset/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>资产统计</template>
          </el-menu-item>
          <el-menu-item index="/asset/port-connection">
            <el-icon><Connection /></el-icon>
            <template #title>端口互联</template>
          </el-menu-item>
          <el-menu-item index="/asset/external-broadband">
            <el-icon><Position /></el-icon>
            <template #title>IPS带宽</template>
          </el-menu-item>
          <el-menu-item index="/asset/license">
            <el-icon><Key /></el-icon>
            <template #title>授权管理</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- IP 管理 -->
        <el-sub-menu index="/ip">
          <template #title>
            <el-icon><Share /></el-icon>
            <span>IP管理</span>
          </template>
          <el-menu-item index="/ip/ip-plan">
            <el-icon><Grid /></el-icon>
            <template #title>IP地址规划</template>
          </el-menu-item>
          <el-menu-item index="/ip/ip-allocation">
            <el-icon><Tickets /></el-icon>
            <template #title>IP地址分配表</template>
          </el-menu-item>
          <el-menu-item index="/ip/interconnect-ip">
            <el-icon><Connection /></el-icon>
            <template #title>互联IP</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- 权限管理 -->
        <el-menu-item index="/permission">
          <el-icon><Lock /></el-icon>
          <template #title>权限管理</template>
        </el-menu-item>

        <!-- 系统管理 -->
        <el-sub-menu index="/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item v-if="userStore.isAdmin" index="/system/user">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/system/role">
            <el-icon><UserFilled /></el-icon>
            <template #title>角色管理</template>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/system/audit">
            <el-icon><Memo /></el-icon>
            <template #title>审计管理</template>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/system/designer">
            <el-icon><EditPen /></el-icon>
            <template #title>表单设计</template>
          </el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/system/fields">
            <el-icon><Files /></el-icon>
            <template #title>字段管理</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- Main content -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="appStore.toggleSidebar" size="20">
            <Fold v-if="!appStore.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-if="route.path !== '/home'" :to="{ path: '/home' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="matched in route.matched.filter(m => m.meta?.title)" :key="matched.path" :to="matched.path !== route.path ? { path: matched.path } : undefined">
              {{ matched.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              <span class="username">{{ userStore.realName || userStore.username }}</span>
              <el-tag v-if="userStore.isAdmin" size="small" type="danger">管理员</el-tag>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { ElMessageBox } from 'element-plus'
import {
  Monitor, DataAnalysis, Connection, Position, Key, Share, Grid, Tickets,
  Lock, Setting, User, UserFilled, Memo, EditPen, HomeFilled, Files,
  Fold, Expand, SwitchButton,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

async function handleCommand(command) {
  if (command === 'logout') {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #3d4d5f;
}

.logo-text {
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  cursor: pointer;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
}

.username {
  font-size: 14px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
