import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAdminStore = defineStore('admin', () => {
  const adminToken = ref(localStorage.getItem('admin_token') || '')
  const adminInfo = ref(JSON.parse(localStorage.getItem('admin_info') || 'null'))

  function setAdminToken(token) {
    adminToken.value = token
    localStorage.setItem('admin_token', token)
  }

  function setAdminInfo(info) {
    adminInfo.value = info
    localStorage.setItem('admin_info', JSON.stringify(info))
  }

  function logout() {
    adminToken.value = ''
    adminInfo.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_info')
  }

  return {
    adminToken,
    adminInfo,
    setAdminToken,
    setAdminInfo,
    logout
  }
})
