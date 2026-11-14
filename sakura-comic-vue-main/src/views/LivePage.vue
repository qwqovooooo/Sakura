<template>
  <div class="live-page">
    <!-- 顶部标题 -->
    <div class="page-header">
      <h1 class="page-title">直播间</h1>
      <el-button type="primary" @click="goToMyRoom" class="my-room-btn">
        我的直播间
      </el-button>
    </div>

    <!-- 分类筛选 -->
    <div class="category-filter">
      <el-radio-group v-model="selectedCategory" @change="loadLiveRooms">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button label="娱乐">娱乐</el-radio-button>
        <el-radio-button label="游戏">游戏</el-radio-button>
        <el-radio-button label="音乐">音乐</el-radio-button>
        <el-radio-button label="学习">学习</el-radio-button>
        <el-radio-button label="其他">其他</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 直播间列表 -->
    <div v-loading="loading" class="live-room-grid">
      <div
        v-for="room in liveRooms"
        :key="room.id"
        class="live-room-card"
        @click="enterRoom(room.room_id)"
      >
        <div class="room-cover">
          <img :src="room.cover_image || '/imgs/default-cover.jpg'" :alt="room.title">
          <div class="live-badge">直播中</div>
          <div class="viewer-count">
            <el-icon><View /></el-icon>
            <span>{{ formatViewerCount(room.viewer_count) }}</span>
          </div>
        </div>
        <div class="room-info">
          <h3 class="room-title">{{ room.title }}</h3>
          <div class="room-meta">
            <span class="anchor-name">{{ room.anchor_name }}</span>
            <span class="category-tag">{{ room.category }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && liveRooms.length === 0" class="empty-state">
      <div class="empty-icon">暂无直播</div>
      <p>当前没有正在直播的房间</p>
      <el-button type="primary" @click="goToMyRoom">
        创建我的直播间
      </el-button>
    </div>

    <!-- 分页 -->
    <div v-if="total > pageSize" class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadLiveRooms"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import { getLiveRoomList } from '../apis/live'

const router = useRouter()

const loading = ref(false)
const liveRooms = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const selectedCategory = ref('')

// 加载直播间列表
const loadLiveRooms = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      only_live: true
    }
    
    if (selectedCategory.value) {
      params.category = selectedCategory.value
    }
    
    const response = await getLiveRoomList(params)
    if (response && Array.isArray(response)) {
      liveRooms.value = response
      total.value = response.length // 注意：实际应该从响应中获取总数
    }
  } catch (error) {
    console.error('加载直播间列表失败:', error)
    ElMessage.error('加载直播间列表失败')
  } finally {
    loading.value = false
  }
}

// 格式化观看人数
const formatViewerCount = (count) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + '万'
  }
  return count
}

// 进入直播间
const enterRoom = (roomId) => {
  router.push(`/live/room/${roomId}`)
}

// 前往我的直播间
const goToMyRoom = () => {
  router.push('/live/my-room')
}

onMounted(() => {
  loadLiveRooms()
  
  // 每30秒刷新一次列表
  setInterval(() => {
    loadLiveRooms()
  }, 30000)
})
</script>

<style scoped>
.live-page {
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #5C3317;
  margin: 0;
  letter-spacing: 1px;
}

.my-room-btn {
  background: linear-gradient(135deg, #FF9A3C 0%, #FF6B35 100%);
  border: none;
  padding: 12px 28px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
}

/* 分类筛选 */
.category-filter {
  margin-bottom: 30px;
}

.category-filter :deep(.el-radio-button__inner) {
  background: rgba(255, 248, 235, 0.6);
  border-color: rgba(255, 173, 96, 0.3);
  color: #8B5A2B;
  font-weight: 500;
}

.category-filter :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #FF9A3C 0%, #FF6B35 100%);
  border-color: #FF9A3C;
  color: white;
  box-shadow: 0 2px 8px rgba(255, 154, 60, 0.3);
}

/* 直播间网格 */
.live-room-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.live-room-card {
  background: rgba(255, 248, 235, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid rgba(255, 173, 96, 0.2);
}

.live-room-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(255, 154, 60, 0.25);
  border-color: rgba(255, 154, 60, 0.4);
}

.room-cover {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  background: #f5f5f5;
  overflow: hidden;
}

.room-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.live-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  background: linear-gradient(135deg, #FF5C8D 0%, #FF3366 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(255, 51, 102, 0.4);
}

.viewer-count {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.room-info {
  padding: 16px;
}

.room-title {
  font-size: 16px;
  font-weight: 600;
  color: #5C3317;
  margin: 0 0 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.anchor-name {
  color: #8B5A2B;
  font-weight: 500;
}

.category-tag {
  background: rgba(255, 192, 128, 0.3);
  color: #FF6B35;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  color: #C19875;
  margin-bottom: 20px;
}

.empty-state p {
  font-size: 16px;
  color: #8B5A2B;
  margin-bottom: 24px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.pagination :deep(.el-pagination button),
.pagination :deep(.el-pager li) {
  background: rgba(255, 248, 235, 0.6);
  color: #8B5A2B;
}

.pagination :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #FF9A3C 0%, #FF6B35 100%);
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .live-page {
    padding: 20px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .page-title {
    font-size: 24px;
  }

  .live-room-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
}
</style>
