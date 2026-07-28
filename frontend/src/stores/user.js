import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, logout as apiLogout, getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.is_admin || false)
  const username = computed(() => userInfo.value?.username || '')
  const realName = computed(() => userInfo.value?.real_name || '')

  async function login(credentials) {
    const data = await apiLogin(credentials)
    token.value = data.access_token
    userInfo.value = data.user
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('userInfo', JSON.stringify(data.user))
    return data
  }

  async function logout() {
    try {
      await apiLogout()
    } catch {
      // Ignore logout API errors
    }
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  async function fetchCurrentUser() {
    try {
      const data = await getCurrentUser()
      userInfo.value = data
      localStorage.setItem('userInfo', JSON.stringify(data))
      return data
    } catch {
      logout()
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    username,
    realName,
    login,
    logout,
    fetchCurrentUser,
  }
})
