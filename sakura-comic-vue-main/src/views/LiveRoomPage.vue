<template>
  <div class="live-room-page">
    <div v-loading="loading" class="live-container">
      <!-- 左侧：视频播放器 -->
      <div class="player-section">
        <div class="video-wrapper">
          <!-- 抖音等不支持iframe的平台，显示跳转按钮 -->
          <div
            v-if="room?.source_type === 'external' && isDouyinOrUnsupportedPlatform(room?.source_url)"
            class="external-link-overlay"
          >
            <div class="link-content">
              <div class="link-icon">📱</div>
              <h3>该平台不支持网页嵌入</h3>
              <p>点击下方按钮前往{{ getPlatformName(room?.source_url) }}观看直播</p>
              <el-button 
                type="primary" 
                size="large"
                @click="openExternalLink(room?.source_url)"
              >
                前往观看直播
              </el-button>
            </div>
          </div>
          
          <!-- 支持iframe的外部直播源 -->
          <iframe
            v-else-if="room?.source_type === 'external' && room?.source_url"
            :src="room.source_url"
            class="external-player"
            frameborder="0"
            allowfullscreen
            allow="autoplay; encrypted-media"
          ></iframe>
          
          <!-- 本地直播源（FLV） -->
          <video
            v-else
            ref="videoElement"
            class="live-player"
            controls
            autoplay
            muted
          ></video>
          
          <div v-if="!room?.is_live && room?.source_type !== 'external'" class="offline-overlay">
            <div class="offline-text">主播暂未开播</div>
          </div>
        </div>

        <!-- 直播间信息 -->
        <div class="room-info-panel">
          <div class="info-left">
            <h2 class="room-title">{{ room?.title }}</h2>
            <div class="room-stats">
              <span class="stat-item">
                <el-icon><View /></el-icon>
                {{ room?.viewer_count || 0 }} 人观看
              </span>
              <span class="stat-item">
                <el-icon><Star /></el-icon>
                {{ room?.like_count || 0 }} 点赞
              </span>
              <span class="category-badge">{{ room?.category }}</span>
            </div>
          </div>
          <div class="info-right">
            <el-button type="danger" :icon="Star" @click="likeRoom" class="like-btn">
              点赞
            </el-button>
          </div>
        </div>

        <!-- 主播信息 -->
        <div class="anchor-info">
          <div class="anchor-avatar">
            {{ room?.anchor_name?.charAt(0) }}
          </div>
          <div class="anchor-details">
            <div class="anchor-name">{{ room?.anchor_name }}</div>
            <div class="anchor-desc">{{ room?.description || '暂无简介' }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧：聊天区域 -->
      <div class="chat-section">
        <!-- 聊天室 -->
        <div class="chat-container">
          <div class="chat-header">
            <h3>聊天室</h3>
            <span class="online-count">{{ room?.viewer_count || 0 }} 人在线</span>
          </div>

          <div class="chat-messages" ref="chatMessages">
            <div v-for="(msg, index) in messages" :key="index" class="chat-message">
              <span class="message-user">{{ msg.user }}:</span>
              <span class="message-text">{{ msg.text }}</span>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="messageInput"
              placeholder="说点什么..."
              @keyup.enter="sendMessage"
              :disabled="!isLogin"
            >
              <template #append>
                <el-button @click="sendMessage" :disabled="!isLogin">
                  发送
                </el-button>
              </template>
            </el-input>
            <div v-if="!isLogin" class="login-hint">
              请先<a href="/login">登录</a>后发言
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：直播带货商品管理（横向全屏） -->
    <div class="products-manage-full-width">
      <div class="products-header">
        <h3>直播间商品管理</h3>
        <el-button type="primary" size="small" @click="showAddDialog">
          <el-icon><Plus /></el-icon> 添加商品
        </el-button>
      </div>
      
      <div v-if="products.length === 0" class="no-products">
        <p>暂无商品，点击上方按钮添加</p>
      </div>
      
      <!-- 商品表格 -->
      <el-table v-else :data="products" style="width: 100%;" stripe>
        <el-table-column type="index" label="序号" width="80" />
        
        <el-table-column label="商品图片" width="120">
          <template #default="{row}">
            <img 
              :src="row.product_image || '/imgs/详情页.png'" 
              style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px;"
            >
          </template>
        </el-table-column>
        
        <el-table-column prop="product_name" label="商品名称" width="200" />
        
        <el-table-column prop="description" label="描述" min-width="250" show-overflow-tooltip />
        
        <el-table-column label="价格" width="150">
          <template #default="{row}">
            <div style="display: flex; flex-direction: column; gap: 4px;">
              <span style="color: #ff4757; font-weight: 600;">￥{{ row.price }}</span>
              <span v-if="row.original_price" style="color: #999; font-size: 12px; text-decoration: line-through;">
                ￥{{ row.original_price }}
              </span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="stock" label="库存" width="100" />
        
        <el-table-column label="状态" width="110">
          <template #default="{row}">
            <el-tag 
              :type="row.is_active === 1 ? 'success' : 'info'"
              style="cursor: default;"
            >
              {{ row.is_active === 1 ? '已上架' : '已下架' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280">
          <template #default="{row}">
            <el-button 
              size="small" 
              :type="row.is_active === 1 ? 'warning' : 'success'"
              @click="toggleProductStatus(row)"
            >
              {{ row.is_active === 1 ? '下架' : '上架' }}
            </el-button>
            <el-button size="small" @click="editProduct(row)">
              编辑
            </el-button>
            <el-button size="small" type="danger" @click="deleteProduct(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

      <!-- 添加/编辑商品对话框 -->
        <el-dialog 
          v-model="productDialogVisible" 
          :title="isEditingProduct ? '编辑商品' : '添加商品'"
          width="600px"
        >
          <el-form :model="productForm" label-width="100px">
            <el-form-item label="商品名称" required>
              <el-input v-model="productForm.product_name" placeholder="请输入商品名称" />
            </el-form-item>
            
            <el-form-item label="商品描述">
              <el-input 
                v-model="productForm.description" 
                type="textarea" 
                :rows="3"
                placeholder="请输入商品描述"
              />
            </el-form-item>
            
            <el-form-item label="商品价格" required>
              <el-input-number 
                v-model="productForm.price" 
                :precision="2" 
                :step="0.1" 
                :min="0"
                style="width: 100%;"
              />
            </el-form-item>
            
            <el-form-item label="原价">
              <el-input-number 
                v-model="productForm.original_price" 
                :precision="2" 
                :step="0.1" 
                :min="0"
                style="width: 100%;"
                placeholder="可选"
              />
            </el-form-item>
            
            <el-form-item label="库存" required>
              <el-input-number 
                v-model="productForm.stock" 
                :min="0"
                style="width: 100%;"
              />
            </el-form-item>
            
            <el-form-item label="商品图片">
              <el-input 
                v-model="productForm.product_image" 
                placeholder="请输入图片链接"
              />
              <div style="margin-top: 8px; font-size: 12px; color: #999;">
                示例：/imgs/详情页.png 或 https://example.com/product.jpg
              </div>
            </el-form-item>
            
            <el-form-item label="购买链接" required>
              <el-input 
                v-model="productForm.purchase_link" 
                placeholder="请输入商品购买链接"
              />
              <div style="margin-top: 8px; font-size: 12px; color: #999;">
                示例：https://taobao.com/item/123456
              </div>
            </el-form-item>
            
            <el-form-item label="排序">
              <el-input-number 
                v-model="productForm.sort_order" 
                :min="0"
                style="width: 100%;"
              />
            </el-form-item>
            
            <el-form-item label="上架状态">
              <el-switch 
                v-model="productForm.is_active" 
                :active-value="1" 
                :inactive-value="0"
                active-text="上架"
                inactive-text="下架"
              />
            </el-form-item>
          </el-form>
          
          <template #footer>
            <el-button @click="productDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSaveProduct" :loading="savingProduct">
              {{ isEditingProduct ? '保存' : '添加' }}
            </el-button>
          </template>
        </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Star, Plus, Edit, Delete, Box, ShoppingCart, Goods } from '@element-plus/icons-vue'
import { getLiveRoomDetail } from '../apis/live'

const route = useRoute()
const roomId = route.params.roomId

const loading = ref(true)
const room = ref(null)
const videoElement = ref(null)
let flvPlayer = null

const messages = ref([
  { user: '系统', text: '欢迎来到直播间' }
])
const messageInput = ref('')
const chatMessages = ref(null)

// 商品列表
const products = ref([])

// 商品管理相关
const productDialogVisible = ref(false)
const isEditingProduct = ref(false)
const savingProduct = ref(false)
const currentEditingProductId = ref(null)

const productForm = ref({
  product_name: '',
  description: '',
  price: 0,
  original_price: null,
  stock: 0,
  product_image: '',
  purchase_link: '',
  sort_order: 0,
  is_active: 1
})

// 检查是否登录
const isLogin = computed(() => {
  return !!localStorage.getItem('token')
})

// 已上架商品数量
const activeProductsCount = computed(() => {
  return products.value.filter(p => p.is_active === 1).length
})

// 已下架商品数量
const inactiveProductsCount = computed(() => {
  return products.value.filter(p => p.is_active === 0).length
})

// 已上架商品的总剩余库存
const totalActiveStock = computed(() => {
  return products.value
    .filter(p => p.is_active === 1)
    .reduce((sum, p) => sum + (p.stock || 0), 0)
})

// 加载直播间信息
const loadRoomInfo = async () => {
  loading.value = true
  try {
    const response = await getLiveRoomDetail(roomId)
    if (response) {
      room.value = response
      
      // 如果直播中，初始化播放器
      if (response.is_live && response.flv_url) {
        initPlayer(response.flv_url)
      }
    }
  } catch (error) {
    console.error('加载直播间信息失败:', error)
    ElMessage.error('加载直播间信息失败')
  } finally {
    loading.value = false
  }
}

// 初始化FLV播放器
const initPlayer = async (url) => {
  try {
    // 动态导入 flv.js
    const flvjs = await import('flv.js')
    
    if (flvjs.default.isSupported()) {
      flvPlayer = flvjs.default.createPlayer({
        type: 'flv',
        url: url,
        isLive: true,
        hasAudio: true,
        hasVideo: true
      })
      
      flvPlayer.attachMediaElement(videoElement.value)
      flvPlayer.load()
      
      // 自动播放
      flvPlayer.play().catch(() => {
        ElMessage.warning('请点击播放按钮开始观看')
      })
    } else {
      ElMessage.error('您的浏览器不支持FLV播放')
    }
  } catch (error) {
    console.error('初始化播放器失败:', error)
    ElMessage.error('播放器初始化失败，请刷新页面重试')
  }
}

// 点赞直播间
const likeRoom = () => {
  if (!room.value) return
  room.value.like_count++
  ElMessage.success('点赞成功')
}

// 加载商品列表
const loadProducts = async () => {
  if (!room.value) return
  
  try {
    const response = await fetch(`http://127.0.0.1:8000/live/products/${room.value.id}`)
    const data = await response.json()
    
    if (data.success) {
      products.value = data.products
    }
  } catch (error) {
    console.error('加载商品失败:', error)
  }
}

// 打开商品链接
const openProductLink = (product) => {
  if (product.purchase_link && product.stock > 0 && product.is_active) {
    window.open(product.purchase_link, '_blank')
  } else if (product.stock === 0) {
    ElMessage.warning('商品已售罄')
  } else if (!product.is_active) {
    ElMessage.warning('商品已下架')
  } else {
    ElMessage.info('暂无购买链接')
  }
}

// 显示添加对话框
const showAddDialog = () => {
  isEditingProduct.value = false
  productForm.value = {
    product_name: '',
    description: '',
    price: 0,
    original_price: null,
    stock: 0,
    product_image: '/imgs/详情页.png',
    purchase_link: '',
    sort_order: 0,
    is_active: 1
  }
  productDialogVisible.value = true
}

// 编辑商品
const editProduct = (product) => {
  isEditingProduct.value = true
  currentEditingProductId.value = product.id
  productForm.value = {
    product_name: product.product_name,
    description: product.description,
    price: parseFloat(product.price),
    original_price: product.original_price ? parseFloat(product.original_price) : null,
    stock: product.stock,
    product_image: product.product_image,
    purchase_link: product.purchase_link,
    sort_order: product.sort_order,
    is_active: product.is_active
  }
  productDialogVisible.value = true
}

// 保存商品
const handleSaveProduct = async () => {
  if (!productForm.value.product_name) {
    ElMessage.warning('请输入商品名称')
    return
  }
  
  if (!productForm.value.purchase_link) {
    ElMessage.warning('请输入购买链接')
    return
  }
  
  savingProduct.value = true
  
  try {
    const url = isEditingProduct.value 
      ? `http://127.0.0.1:8000/live/products/${currentEditingProductId.value}`
      : 'http://127.0.0.1:8000/live/products/add'
    
    const response = await fetch(url, {
      method: isEditingProduct.value ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(productForm.value)
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success(isEditingProduct.value ? '修改成功' : '添加成功')
      productDialogVisible.value = false
      await loadProducts()
    } else {
      ElMessage.error(data.message || '操作失败')
    }
  } catch (error) {
    console.error('保存商品失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    savingProduct.value = false
  }
}

// 删除商品
const deleteProduct = async (productId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const token = localStorage.getItem('token')
    const response = await fetch(`http://127.0.0.1:8000/live/products/${productId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success('删除成功')
      await loadProducts()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除商品失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

// 切换商品上下架状态
const toggleProductStatus = async (product) => {
  // 先保存原状态
  const oldStatus = product.is_active
  // 切换状态
  product.is_active = oldStatus === 1 ? 0 : 1
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://127.0.0.1:8000/live/products/${product.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        product_name: product.product_name,
        description: product.description,
        price: parseFloat(product.price),
        original_price: product.original_price ? parseFloat(product.original_price) : null,
        stock: product.stock,
        product_image: product.product_image,
        purchase_link: product.purchase_link,
        sort_order: product.sort_order,
        is_active: product.is_active
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success(product.is_active === 1 ? '已上架' : '已下架')
    } else {
      // 恢复状态
      product.is_active = oldStatus
      ElMessage.error(data.message || '操作失败')
    }
  } catch (error) {
    console.error('切换状态失败:', error)
    // 恢复状态
    product.is_active = oldStatus
    ElMessage.error('操作失败，请重试')
  }
}

// 发送消息
const sendMessage = () => {
  if (!messageInput.value.trim()) return
  
  const userName = localStorage.getItem('user_name') || '游客'
  messages.value.push({
    user: userName,
    text: messageInput.value
  })
  
  messageInput.value = ''
  
  // 滚动到底部
  setTimeout(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  }, 100)
}

// 检查是否是抖音或其他不支持iframe的平台
const isDouyinOrUnsupportedPlatform = (url) => {
  if (!url) return false
  const unsupportedDomains = [
    'douyin.com',
    'v.douyin.com',
    'tiktok.com',
    'kuaishou.com'
  ]
  return unsupportedDomains.some(domain => url.includes(domain))
}

// 获取平台名称
const getPlatformName = (url) => {
  if (!url) return '直播平台'
  if (url.includes('douyin')) return '抖音'
  if (url.includes('tiktok')) return 'TikTok'
  if (url.includes('kuaishou')) return '快手'
  return '直播平台'
}

// 打开外部链接
const openExternalLink = (url) => {
  if (!url) return
  window.open(url, '_blank')
}

onMounted(() => {
  loadRoomInfo()
  // 加载商品列表
  setTimeout(() => {
    loadProducts()
  }, 1000)
})

onUnmounted(() => {
  if (flvPlayer) {
    flvPlayer.destroy()
  }
})
</script>

<style scoped>
.live-room-page {
  min-height: 100vh;
  padding: 20px;
  width: 100%;
  max-width: 100vw;
  overflow-x: hidden;
  box-sizing: border-box;
}

.live-container {
  max-width: 100%;
  width: 100%;
  margin: 0 auto;
  display: flex;
  gap: 20px;
  box-sizing: border-box;
}

/* 播放器区域 */
.player-section {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-wrapper {
  position: relative;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
}

.live-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.external-player {
  width: 100%;
  height: 100%;
  border: none;
}

.external-link-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.link-content {
  text-align: center;
  color: white;
  max-width: 500px;
}

.link-icon {
  font-size: 80px;
  margin-bottom: 20px;
  animation: bounce 2s infinite;
}

.link-content h3 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
}

.link-content p {
  font-size: 16px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.link-content .el-button {
  background: white;
  color: #667eea;
  border: none;
  font-size: 16px;
  font-weight: 600;
  padding: 16px 40px;
  border-radius: 50px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.link-content .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.offline-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.offline-text {
  color: white;
  font-size: 24px;
  font-weight: 600;
}

/* 直播间信息 */
.room-info-panel {
  background: rgba(255, 248, 235, 0.85);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 2px solid rgba(255, 173, 96, 0.3);
}

.room-title {
  font-size: 24px;
  font-weight: 700;
  color: #5C3317;
  margin: 0 0 10px 0;
}

.room-stats {
  display: flex;
  gap: 16px;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #8B5A2B;
  font-size: 14px;
}

.category-badge {
  background: rgba(255, 154, 60, 0.2);
  color: #FF6B35;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.like-btn {
  background: linear-gradient(135deg, #FF5C8D 0%, #FF3366 100%);
  border: none;
  color: white;
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
}

/* 主播信息 */
.anchor-info {
  background: rgba(255, 248, 235, 0.85);
  backdrop-filter: blur(10px);
  padding: 16px;
  border-radius: 12px;
  display: flex;
  gap: 12px;
  border: 2px solid rgba(255, 173, 96, 0.3);
}

.anchor-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF9A3C 0%, #FF6B35 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  flex-shrink: 0;
}

.anchor-details {
  flex: 1;
}

.anchor-name {
  font-size: 16px;
  font-weight: 600;
  color: #5C3317;
  margin-bottom: 4px;
}

.anchor-desc {
  font-size: 14px;
  color: #8B5A2B;
}

/* 聊天区域 */
.chat-section {
  width: 380px;
  flex-shrink: 0;
  background: rgba(255, 248, 235, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  height: fit-content;
  min-height: 600px;
  max-height: calc(100vh - 40px);
  border: 2px solid rgba(255, 173, 96, 0.3);
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 2px solid rgba(255, 173, 96, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #5C3317;
  margin: 0;
}

.online-count {
  font-size: 13px;
  color: #8B5A2B;
  background: rgba(255, 192, 128, 0.3);
  padding: 4px 10px;
  border-radius: 6px;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  min-height: 0;
}

.chat-message {
  margin-bottom: 12px;
  line-height: 1.6;
}

.message-user {
  color: #FF6B35;
  font-weight: 600;
  margin-right: 6px;
}

.message-text {
  color: #5C3317;
}

.chat-input {
  flex-shrink: 0;
  padding: 16px;
  border-top: 2px solid rgba(255, 173, 96, 0.3);
  background: white;
}

.login-hint {
  margin-top: 8px;
  font-size: 13px;
  color: #8B5A2B;
  text-align: center;
}

.login-hint a {
  color: #FF6B35;
  text-decoration: none;
  font-weight: 600;
}

/* 商品管理区域样式 */
.products-manage-section {
  margin-top: 24px;
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  max-width: 100%;
  overflow: hidden;
}

.products-manage-section .products-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 173, 96, 0.2);
}

.products-manage-section .products-header h3 {
  font-size: 20px;
  font-weight: 700;
  color: #5C3317;
  margin: 0;
}

.products-manage-section .no-products {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 15px;
}

/* 商品内容区域布局 */
.products-content {
  display: flex;
  gap: 20px;
  align-items: flex-start;
  max-width: 100%;
  overflow: hidden;
  width: 100%;
}

.products-table-container {
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  max-width: 100%;
}

/* 统计卡片 */
.products-stats-card {
  width: 240px;
  background: linear-gradient(135deg, #FFE5B4 0%, #FFB347 50%, #FFA500 100%);
  border-radius: 20px;
  padding: 20px;
  color: #5C3317;
  box-shadow: 0 12px 32px rgba(255, 165, 0, 0.4);
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.6);
}

.products-stats-card::before {
  content: '';
  position: absolute;
  top: -80px;
  right: -80px;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.25) 0%, transparent 70%);
  border-radius: 50%;
  z-index: 0;
}

.products-stats-card::after {
  content: '';
  position: absolute;
  bottom: -40px;
  left: -40px;
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 60%);
  border-radius: 50%;
  z-index: 0;
}

.stats-title {
  font-size: 17px;
  font-weight: 800;
  margin-bottom: 24px;
  text-align: center;
  padding-bottom: 18px;
  border-bottom: 2px solid rgba(92, 51, 23, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
  letter-spacing: 0.5px;
}

.stats-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 28px 0;
  position: relative;
  z-index: 1;
}

.stats-icon-wrapper {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.2) 100%);
  border-radius: 50%;
  width: 90px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 20px rgba(92, 51, 23, 0.2), inset 0 2px 8px rgba(255, 255, 255, 0.5);
  border: 3px solid rgba(255, 255, 255, 0.6);
  transition: transform 0.3s ease;
}

.stats-icon-wrapper:hover {
  transform: scale(1.05) rotate(5deg);
}

.stats-icon {
  color: #5C3317;
  opacity: 0.8;
}

.stats-count {
  text-align: right;
}

.count-number {
  font-size: 52px;
  font-weight: 900;
  line-height: 1;
  color: #5C3317;
  text-shadow: 3px 3px 6px rgba(92, 51, 23, 0.15), 0 0 20px rgba(255, 255, 255, 0.5);
  background: linear-gradient(180deg, #5C3317 0%, #8B4513 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.count-label {
  font-size: 14px;
  margin-top: 10px;
  opacity: 0.85;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.stats-stock {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0.3) 100%);
  border-radius: 14px;
  padding: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  font-weight: 700;
  position: relative;
  z-index: 1;
  box-shadow: 0 4px 12px rgba(92, 51, 23, 0.15), inset 0 2px 4px rgba(255, 255, 255, 0.5);
  border: 2px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.stats-stock:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(92, 51, 23, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.5);
}

.stats-stock .el-icon {
  margin-right: 8px;
}

.stock-number {
  font-size: 28px;
  font-weight: 900;
  color: #FF6B35;
  margin-left: auto;
  text-shadow: 2px 2px 4px rgba(255, 107, 53, 0.2);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.stats-divider {
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, rgba(92, 51, 23, 0.3) 50%, transparent 100%);
  margin: 24px 0;
  position: relative;
  z-index: 1;
}

.stats-secondary {
  display: flex;
  gap: 14px;
  position: relative;
  z-index: 1;
}

.secondary-item {
  flex: 1;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0.2) 100%);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  box-shadow: 0 2px 8px rgba(92, 51, 23, 0.1);
  transition: all 0.3s ease;
}

.secondary-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(92, 51, 23, 0.15);
}

.secondary-label {
  font-size: 13px;
  opacity: 0.85;
  font-weight: 600;
}

.secondary-value {
  font-size: 26px;
  font-weight: 800;
  color: #5C3317;
  text-shadow: 1px 1px 2px rgba(92, 51, 23, 0.1);
}

/* 表格样式优化 */
.products-manage-section :deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
  font-size: 14px;
}

.products-manage-section :deep(.el-table th) {
  background-color: #FFF8EB;
  color: #5C3317;
  font-weight: 600;
}

.products-manage-section :deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: #FFFBF5;
}

.products-manage-section :deep(.el-table td, .el-table th) {
  padding: 14px 0;
}

.products-manage-section :deep(.el-table .cell) {
  padding-left: 12px;
  padding-right: 12px;
}

.products-manage-section :deep(.el-button--small) {
  padding: 6px 14px;
  font-size: 13px;
}

.products-manage-section :deep(.el-tag) {
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.products-manage-section :deep(.el-tag--success) {
  background-color: #67c23a;
  color: white;
  border-color: #67c23a;
}

.products-manage-section :deep(.el-tag--success:hover) {
  background-color: #85ce61;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.3);
}

.products-manage-section :deep(.el-tag--info) {
  background-color: #909399;
  color: white;
  border-color: #909399;
}

.products-manage-section :deep(.el-tag--info:hover) {
  background-color: #a6a9ad;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(144, 147, 153, 0.3);
}

/* 滚动条 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(255, 154, 60, 0.4);
  border-radius: 3px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .live-container {
    grid-template-columns: 1fr;
  }
  
  .chat-section {
    max-height: 500px;
  }
}

/* 商品列表样式 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  min-height: 500px;
}

.product-count {
  font-size: 14px;
  color: #999;
}

.no-products {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.products-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.product-card {
  display: flex;
  flex-direction: column;
  background: #fafafa;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  height: 280px;
}

.product-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #ff9a3c;
}

.product-image {
  position: relative;
  width: 100%;
  height: 160px;
  flex-shrink: 0;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stock-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 154, 60, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.stock-badge.sold-out {
  background: rgba(153, 153, 153, 0.9);
}

.product-info {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  position: relative;
}

.product-name {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-price {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.current-price {
  font-size: 18px;
  font-weight: 700;
  color: #ff4757;
}

.original-price {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
}

.buy-btn {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-weight: 600;
}

.products-list::-webkit-scrollbar {
  width: 6px;
}

.products-list::-webkit-scrollbar-thumb {
  background: rgba(255, 154, 60, 0.4);
  border-radius: 3px;
}

/* 底部商品管理区域（横向全屏） */
.products-manage-full-width {
  margin-top: 30px;
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.products-manage-full-width .products-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.products-manage-full-width .products-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.products-manage-full-width .no-products {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}
</style>
