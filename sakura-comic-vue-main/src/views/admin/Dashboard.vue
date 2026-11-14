<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-container">
      <div class="stat-card user-card">
        <div class="stat-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">总用户数</div>
          <div class="stat-value">{{ stats.totalUsers }}</div>
        </div>
      </div>

      <div class="stat-card movie-card">
        <div class="stat-icon">
          <el-icon><VideoCamera /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">视频总数</div>
          <div class="stat-value">{{ stats.totalMovies }}</div>
        </div>
      </div>

      <div class="stat-card comment-card">
        <div class="stat-icon">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">评论总数</div>
          <div class="stat-value">{{ stats.totalComments }}</div>
        </div>
      </div>

      <div class="stat-card admin-card">
        <div class="stat-icon">
          <el-icon><UserFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">管理员数</div>
          <div class="stat-value">{{ stats.adminUsers }}</div>
        </div>
      </div>
    </div>

    <!-- 欢迎卡片 -->
    <div class="welcome-section">
      <el-card class="welcome-card" shadow="never">
        <template #header>
          <div class="welcome-header">
            <span class="welcome-title">欢迎使用 Sakura 管理后台</span>
          </div>
        </template>

        <div class="welcome-content">
          <p class="welcome-desc">
            <el-icon><SuccessFilled /></el-icon>
            这是一个功能完善的视频网站管理系统，帮助你轻松管理用户、视频和评论。
          </p>

          <el-divider />

          <div class="features-section">
            <h4 class="features-title">主要功能</h4>
            <div class="features-grid">
              <div class="feature-item">
                <el-icon class="feature-icon user-icon"><User /></el-icon>
                <div class="feature-text">
                  <div class="feature-name">用户管理</div>
                  <div class="feature-desc">管理用户、分配权限、查看统计</div>
                </div>
              </div>

              <div class="feature-item">
                <el-icon class="feature-icon movie-icon"><VideoCamera /></el-icon>
                <div class="feature-text">
                  <div class="feature-name">视频管理</div>
                  <div class="feature-desc">新增、编辑、删除视频内容</div>
                </div>
              </div>

              <div class="feature-item">
                <el-icon class="feature-icon comment-icon"><ChatDotRound /></el-icon>
                <div class="feature-text">
                  <div class="feature-name">评论管理</div>
                  <div class="feature-desc">审核、删除和管理用户评论</div>
                </div>
              </div>
            </div>
          </div>

          <el-divider />

          <div class="quick-nav">
            <h4 class="nav-title">快速导航</h4>
            <div class="nav-buttons">
              <el-button type="primary" size="large" @click="$router.push('/admin/users')" class="nav-btn">
                <el-icon><User /></el-icon>
                前往用户管理
              </el-button>
              <el-button type="success" size="large" @click="$router.push('/admin/movies')" class="nav-btn">
                <el-icon><VideoCamera /></el-icon>
                前往视频管理
              </el-button>
              <el-button type="warning" size="large" @click="$router.push('/admin/comments')" class="nav-btn">
                <el-icon><ChatDotRound /></el-icon>
                前往评论管理
              </el-button>
              <el-button @click="$router.push('/')" class="nav-btn home-btn">
                <el-icon><HomeFilled /></el-icon>
                返回前台
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User, VideoCamera, ChatDotRound, UserFilled, HomeFilled, SuccessFilled } from '@element-plus/icons-vue'
import { getUserList, getMovieList, getCommentList } from '../../apis/admin'

const stats = ref({
  totalUsers: 0,
  totalMovies: 0,
  totalComments: 0,
  adminUsers: 0
})

const loadStats = async () => {
  try {
    // 获取用户统计
    const userRes = await getUserList({ page: 1, page_size: 1 })
    if (userRes.code === 200) {
      stats.value.totalUsers = userRes.data.total
      stats.value.adminUsers = userRes.data.admin_count || 0
    }
    
    // 获取视频统计
    const movieRes = await getMovieList({ page: 1, page_size: 1 })
    if (movieRes.code === 200) {
      stats.value.totalMovies = movieRes.data.total
    }
    
    // 获取评论统计
    const commentRes = await getCommentList({ page: 1, page_size: 1 })
    if (commentRes.code === 200) {
      stats.value.totalComments = commentRes.data.total
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 30px;
  background: transparent;
  min-height: 100vh;
}

/* 统计卡片容器 */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

/* 统计卡片 */
.stat-card {
  background: rgba(255, 248, 235, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(139, 90, 60, 0.15);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: 2px solid rgba(255, 173, 96, 0.3);
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 12px 32px rgba(255, 154, 60, 0.25);
  border-color: rgba(255, 154, 60, 0.5);
  background: rgba(255, 248, 235, 0.95);
}

.stat-icon {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card.user-card .stat-icon {
  background: linear-gradient(135deg, #FF9A3C 0%, #FF6B35 100%);
  color: white;
}

.stat-card.movie-card .stat-icon {
  background: linear-gradient(135deg, #FF7A9A 0%, #FF5C8D 100%);
  color: white;
}

.stat-card.comment-card .stat-icon {
  background: linear-gradient(135deg, #5CC4E8 0%, #3FA8D6 100%);
  color: white;
}

.stat-card.admin-card .stat-icon {
  background: linear-gradient(135deg, #7DDA8D 0%, #5BC26D 100%);
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 15px;
  color: #8B5A2B;
  margin-bottom: 10px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 38px;
  font-weight: bold;
  color: #5C3317;
  line-height: 1;
  text-shadow: 1px 1px 2px rgba(92, 51, 23, 0.1);
}

/* 欢迎卡片 */
.welcome-section {
  margin-bottom: 30px;
}

.welcome-card {
  background: rgba(255, 248, 235, 0.9);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 2px solid rgba(255, 173, 96, 0.3);
  box-shadow: 0 8px 32px rgba(139, 90, 60, 0.15);
  border-radius: 16px;
  overflow: hidden;
}

.welcome-card :deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(255, 192, 128, 0.4) 0%, rgba(255, 154, 60, 0.3) 100%);
  border-bottom: 2px solid rgba(255, 173, 96, 0.3);
  padding: 20px 24px;
}

.welcome-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
}

.welcome-title {
  color: #5C3317;
  letter-spacing: 1px;
  text-shadow: 1px 1px 2px rgba(255, 154, 60, 0.2);
}

.welcome-content {
  padding: 24px;
}

.welcome-desc {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: #8B5A2B;
  margin: 0;
  line-height: 1.8;
  font-weight: 500;
}

.welcome-desc .el-icon {
  color: #5BC26D;
  font-size: 20px;
  flex-shrink: 0;
}

/* 功能特性网格 */
.features-section {
  margin: 30px 0;
}

.features-title {
  font-size: 18px;
  font-weight: 700;
  color: #5C3317;
  margin-bottom: 20px;
  letter-spacing: 0.5px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.feature-item {
  display: flex;
  gap: 14px;
  padding: 20px;
  background: rgba(255, 240, 220, 0.5);
  border-radius: 12px;
  transition: all 0.3s;
  border: 1px solid rgba(255, 173, 96, 0.2);
}

.feature-item:hover {
  background: rgba(255, 235, 205, 0.7);
  transform: translateX(6px);
  box-shadow: 0 4px 16px rgba(255, 154, 60, 0.15);
  border-color: rgba(255, 154, 60, 0.4);
}

.feature-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.15);
}

.feature-icon.user-icon {
  background: linear-gradient(135deg, #FF9A3C 0%, #FF6B35 100%);
}

.feature-icon.movie-icon {
  background: linear-gradient(135deg, #FF7A9A 0%, #FF5C8D 100%);
}

.feature-icon.comment-icon {
  background: linear-gradient(135deg, #5CC4E8 0%, #3FA8D6 100%);
}

.feature-text {
  flex: 1;
}

.feature-name {
  font-weight: 700;
  color: #5C3317;
  margin-bottom: 6px;
  font-size: 15px;
}

.feature-desc {
  font-size: 13px;
  color: #A0826D;
  line-height: 1.6;
}

/* 快速导航 */
.quick-nav {
  margin: 30px 0;
}

.nav-title {
  font-size: 18px;
  font-weight: 700;
  color: #5C3317;
  margin-bottom: 20px;
  letter-spacing: 0.5px;
}

.nav-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
}

.nav-btn {
  padding: 14px 28px;
  height: auto;
  border-radius: 12px;
  transition: all 0.3s;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.5px;
  border: 2px solid transparent;
}

.nav-btn:not(.home-btn) {
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);
}

.nav-btn:not(.home-btn):hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.nav-btn.home-btn {
  background: rgba(255, 240, 220, 0.6);
  color: #8B5A2B;
  border-color: rgba(255, 173, 96, 0.3);
}

.nav-btn.home-btn:hover {
  background: rgba(255, 230, 200, 0.8);
  color: #5C3317;
  border-color: rgba(255, 154, 60, 0.5);
  transform: translateY(-3px);
}

.nav-btn .el-icon {
  margin-right: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 20px;
  }

  .stats-container {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 30px;
  }

  .stat-card {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }

  .stat-icon {
    width: 64px;
    height: 64px;
    font-size: 26px;
  }

  .stat-value {
    font-size: 28px;
  }

  .features-grid,
  .nav-buttons {
    grid-template-columns: 1fr;
  }
}
</style>
