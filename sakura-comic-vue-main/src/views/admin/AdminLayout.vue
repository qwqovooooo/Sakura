<template>
  <div class="admin-layout">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="240px" class="sidebar">
        <div class="logo">
          <h2>USC20234080407</h2>
          <h3>罗靓</h3>
          <p>管理后台</p>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>控制台</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/movies">
            <el-icon><VideoCamera /></el-icon>
            <span>视频管理</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/comments">
            <el-icon><ChatDotRound /></el-icon>
            <span>评论管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header">
          <div class="header-left">
            <h3>{{ currentTitle }}</h3>
          </div>
          
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-icon><Avatar /></el-icon>
                <span>{{ adminInfo?.name || '管理员' }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="home">
                    <el-icon><HomeFilled /></el-icon>
                    返回前台
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 内容 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useAdminStore } from '../../store/admin'
import { Odometer, User, VideoCamera, ChatDotRound, Avatar, HomeFilled, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const adminStore = useAdminStore()

const adminInfo = computed(() => adminStore.adminInfo)
const activeMenu = computed(() => route.path)

const currentTitle = computed(() => {
  const titleMap = {
    '/admin/dashboard': '控制台',
    '/admin/users': '用户管理',
    '/admin/movies': '视频管理',
    '/admin/comments': '评论管理'
  }
  return titleMap[route.path] || '管理后台'
})

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      adminStore.logout()
      ElMessage.success('已退出登录')
      router.push('/admin/login')
    }).catch(() => {})
  } else if (command === 'home') {
    router.push('/')
  }
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  overflow: hidden;
  background: transparent;
}

.el-container {
  height: 100%;
}

/* 侧边栏样式 */
.sidebar {
  background: rgba(255, 248, 235, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  color: #5C3317;
  box-shadow: 4px 0 24px rgba(139, 90, 60, 0.15);
  overflow-y: auto;
  position: relative;
  border-right: 2px solid rgba(255, 173, 96, 0.3);
}

.sidebar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(255, 154, 60, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.logo {
  padding: 35px 20px;
  text-align: center;
  background: linear-gradient(135deg, rgba(255, 240, 220, 0.6) 0%, rgba(255, 230, 200, 0.4) 100%);
  border-bottom: 2px solid rgba(255, 173, 96, 0.4);
  position: relative;
  overflow: hidden;
}

.logo::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #FF9A3C, #FF6B35, #FF5C8D);
}

.logo h2 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #A0826D;
  letter-spacing: 0.5px;
  line-height: 1.5;
}

.logo h3 {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 800;
  color: #5C3317;
  letter-spacing: 1px;
  text-shadow: 2px 2px 4px rgba(255, 154, 60, 0.2);
}

.logo p {
  margin: 12px 0 0;
  font-size: 14px;
  color: #8B5A2B;
  letter-spacing: 0.8px;
  font-weight: 600;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
  margin-top: 20px;
}

.sidebar-menu .el-menu-item {
  color: #8B5A2B;
  font-size: 15px;
  margin: 8px 14px;
  border-radius: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  padding-left: 18px !important;
  overflow: hidden;
  font-weight: 500;
}

.sidebar-menu .el-menu-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 0;
  background: linear-gradient(180deg, #FF9A3C 0%, #FF6B35 100%);
  border-radius: 0 4px 4px 0;
  transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255, 192, 128, 0.25);
  color: #5C3317;
  box-shadow: 0 2px 8px rgba(255, 154, 60, 0.15);
}

.sidebar-menu .el-menu-item:hover::before {
  height: 28px;
}

.sidebar-menu .el-menu-item.is-active {
  background: rgba(255, 192, 128, 0.35);
  color: #5C3317;
  font-weight: 700;
  box-shadow: 0 3px 12px rgba(255, 154, 60, 0.2);
}

.sidebar-menu .el-menu-item.is-active::before {
  height: 32px;
}

.sidebar-menu .el-menu-item .el-icon {
  margin-right: 12px;
  color: #C19875;
  transition: all 0.3s;
  font-size: 18px;
}

.sidebar-menu .el-menu-item:hover .el-icon,
.sidebar-menu .el-menu-item.is-active .el-icon {
  color: #FF9A3C;
}

/* 顶部导航 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 248, 235, 0.9);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-bottom: 2px solid rgba(255, 173, 96, 0.3);
  padding: 0 30px;
  box-shadow: 0 4px 16px rgba(139, 90, 60, 0.1);
}

.header-left h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #5C3317;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 10px 18px;
  border-radius: 10px;
  transition: all 0.3s;
  color: #8B5A2B;
  font-weight: 600;
  border: 1px solid transparent;
}

.user-info:hover {
  background: rgba(255, 230, 200, 0.5);
  color: #5C3317;
  border-color: rgba(255, 154, 60, 0.3);
}

.user-info .el-icon {
  font-size: 20px;
  color: #FF9A3C;
}

/* 主内容区 */
.main-content {
  background: transparent;
  overflow-y: auto;
  padding: 30px;
}

/* 滚动条美化 */
.sidebar::-webkit-scrollbar,
.main-content::-webkit-scrollbar {
  width: 8px;
}

.sidebar::-webkit-scrollbar-track,
.main-content::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgba(255, 173, 96, 0.3);
  border-radius: 4px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 154, 60, 0.5);
}

.main-content::-webkit-scrollbar-thumb {
  background: rgba(255, 173, 96, 0.4);
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 154, 60, 0.6);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px !important;
  }

  .logo h2 {
    font-size: 18px;
  }

  .sidebar-menu .el-menu-item {
    font-size: 14px;
  }

  .main-content {
    padding: 20px;
  }
}
</style>