<template>
  <div class="my-live-room-page">
    <div class="page-container">
      <h1 class="page-title">我的直播间</h1>

      <!-- 创建直播间 -->
      <div v-if="!hasRoom && !loading" class="create-room-section">
        <el-card class="create-card">
          <h2>创建你的直播间</h2>
          <p class="hint-text">创建直播间后，即可使用OBS Studio开始直播</p>
          
          <el-form :model="createForm" label-width="100px" class="create-form">
            <el-form-item label="直播类型">
              <el-radio-group v-model="createForm.source_type">
                <el-radio label="self">自己推流</el-radio>
                <el-radio label="external">外部直播</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="直播间标题">
              <el-input
                v-model="createForm.title"
                placeholder="请输入直播间标题"
                maxlength="200"
              />
            </el-form-item>
            
            <el-form-item label="直播简介">
              <el-input
                v-model="createForm.description"
                type="textarea"
                :rows="3"
                placeholder="介绍一下你的直播内容"
              />
            </el-form-item>
            
            <el-form-item label="直播分类">
              <el-select v-model="createForm.category" placeholder="选择分类">
                <el-option label="娱乐" value="娱乐" />
                <el-option label="游戏" value="游戏" />
                <el-option label="音乐" value="音乐" />
                <el-option label="学习" value="学习" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            
            <!-- 外部直播源配置 -->
            <el-form-item v-if="createForm.source_type === 'external'" label="直播源地址">
              <el-input
                v-model="createForm.source_url"
                placeholder="输入B站/抖音/YouTube等直播间地址"
              />
              <div class="hint-text" style="margin-top: 8px; font-size: 12px; color: #8B5A2B;">
                示例：https://live.bilibili.com/123456
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                @click="handleCreateRoom"
                :loading="creating"
                size="large"
              >
                创建直播间
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 直播间控制台 -->
      <div v-if="hasRoom && !loading" class="dashboard">
        <!-- 状态卡片 -->
        <div class="status-cards">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon" :class="{ live: room.is_live }">
                <el-icon v-if="room.is_live"><VideoCamera /></el-icon>
                <el-icon v-else><VideoCamera /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-label">直播状态</div>
                <div class="card-value">{{ room.is_live ? '直播中' : '未开播' }}</div>
              </div>
            </div>
          </el-card>

          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon viewers">
                <el-icon><View /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-label">当前观众</div>
                <div class="card-value">{{ room.viewer_count || 0 }}</div>
              </div>
            </div>
          </el-card>

          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon likes">
                <el-icon><Star /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-label">点赞数</div>
                <div class="card-value">{{ room.like_count || 0 }}</div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 推流配置 -->
        <el-card class="stream-config">
          <template #header>
            <div class="card-header">
              <span>推流配置</span>
              <el-tag v-if="room.is_live" type="success">直播中</el-tag>
              <el-tag v-else type="info">未开播</el-tag>
            </div>
          </template>

          <div class="config-section">
            <div class="config-item">
              <label>直播间ID</label>
              <div class="config-value">
                <span>{{ room.room_id }}</span>
                <el-button text @click="copyText(room.room_id)">复制</el-button>
              </div>
            </div>

            <div class="config-item">
              <label>RTMP服务器地址</label>
              <div class="config-value">
                <span>{{ streamUrl?.rtmp_url || 'rtmp://localhost/live' }}</span>
                <el-button text @click="copyText(streamUrl?.rtmp_url)">复制</el-button>
              </div>
            </div>

            <div class="config-item">
              <label>推流密钥 (Stream Key)</label>
              <div class="config-value">
                <span class="stream-key">{{ streamUrl?.stream_key || '加载中...' }}</span>
                <el-button text @click="copyText(streamUrl?.stream_key)">复制</el-button>
              </div>
            </div>

            <div class="config-item">
              <label>完整推流地址</label>
              <div class="config-value">
                <code class="push-url">{{ streamUrl?.push_url || '加载中...' }}</code>
                <el-button text @click="copyText(streamUrl?.push_url)">复制</el-button>
              </div>
            </div>
          </div>

          <el-alert
            title="使用说明"
            type="info"
            :closable="false"
            class="usage-alert"
          >
            <div class="usage-steps">
              <p>1. 下载并安装 OBS Studio</p>
              <p>2. 在OBS中选择"设置" → "推流"</p>
              <p>3. 服务选择"自定义"</p>
              <p>4. 将上方的服务器地址和推流密钥填入OBS</p>
              <p>5. 点击下方"开始直播"按钮</p>
              <p>6. 在OBS中点击"开始推流"</p>
            </div>
          </el-alert>
        </el-card>

        <!-- 控制按钮 -->
        <div class="control-buttons">
          <el-button
            v-if="!room.is_live"
            type="primary"
            size="large"
            @click="startLive"
            :loading="operating"
          >
            开始直播
          </el-button>
          <el-button
            v-else
            type="danger"
            size="large"
            @click="stopLive"
            :loading="operating"
          >
            结束直播
          </el-button>

          <el-button
            size="large"
            @click="viewLiveRoom"
          >
            查看直播间
          </el-button>
        </div>

        <!-- 直播间信息 -->
        <el-card class="room-info-card">
          <template #header>
            <span>直播间信息</span>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="直播标题">
              {{ room.title }}
            </el-descriptions-item>
            <el-descriptions-item label="分类">
              {{ room.category }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间" :span="2">
              {{ formatDate(room.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="简介" :span="2">
              {{ room.description || '暂无简介' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 商品管理 -->
        <el-card class="products-manage-card">
          <template #header>
            <div class="card-header">
              <span>商品管理</span>
              <el-button type="primary" size="small" @click="showAddProductDialog">
                添加商品
              </el-button>
            </div>
          </template>

          <div v-if="products.length === 0" class="no-products">
            <p>还没有添加商品，点击上方按钮开始添加</p>
          </div>

          <el-table v-else :data="products" style="width: 100%">
            <el-table-column prop="product_image" label="商品图片" width="100">
              <template #default="{row}">
                <img :src="row.product_image || 'https://via.placeholder.com/80'" 
                     style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;">
              </template>
            </el-table-column>
            <el-table-column prop="product_name" label="商品名称" width="180" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="price" label="价格" width="100">
              <template #default="{row}">
                <span style="color: #ff4757; font-weight: 600;">￥{{ row.price }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="stock" label="库存" width="80" />
            <el-table-column label="操作" width="150">
              <template #default="{row}">
                <el-button size="small" @click="editProduct(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteProduct(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

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
              <div class="hint-text" style="margin-top: 8px; font-size: 12px; color: #999;">
                示例：https://example.com/product.jpg
              </div>
            </el-form-item>
            
            <el-form-item label="购买链接" required>
              <el-input 
                v-model="productForm.purchase_link" 
                placeholder="请输入商品购买链接"
              />
              <div class="hint-text" style="margin-top: 8px; font-size: 12px; color: #999;">
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
          </el-form>
          
          <template #footer>
            <el-button @click="productDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSaveProduct" :loading="savingProduct">
              {{ isEditingProduct ? '保存' : '添加' }}
            </el-button>
          </template>
        </el-dialog>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading" size="48"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoCamera, View, Star, Loading } from '@element-plus/icons-vue'
import {
  createLiveRoom,
  getMyLiveRoom,
  getStreamUrl,
  startLive as startLiveApi,
  stopLive as stopLiveApi
} from '../apis/live'

const router = useRouter()

const loading = ref(true)
const hasRoom = ref(false)
const room = ref(null)
const streamUrl = ref(null)
const creating = ref(false)
const operating = ref(false)

// 商品管理相关
const products = ref([])
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
  sort_order: 0
})

const createForm = ref({
  title: '',
  description: '',
  category: '娱乐',
  source_type: 'self',  // self: 自己推流, external: 外部直播
  source_url: ''  // 外部直播源地址
})

// 加载直播间信息
const loadRoomInfo = async () => {
  loading.value = true
  try {
    const response = await getMyLiveRoom()
    if (response) {
      room.value = response
      hasRoom.value = true
      
      // 获取推流地址
      const urlResponse = await getStreamUrl()
      if (urlResponse) {
        streamUrl.value = urlResponse
      }
    }
  } catch (error) {
    console.error('加载直播间信息失败:', error)
    hasRoom.value = false
  } finally {
    loading.value = false
  }
}

// 创建直播间
const handleCreateRoom = async () => {
  if (!createForm.value.title) {
    ElMessage.warning('请输入直播间标题')
    return
  }

  creating.value = true
  try {
    const response = await createLiveRoom(createForm.value)
    if (response) {
      ElMessage.success('直播间创建成功')
      await loadRoomInfo()
    }
  } catch (error) {
    console.error('创建直播间失败:', error)
    ElMessage.error('创建直播间失败')
  } finally {
    creating.value = false
  }
}

// 开始直播
const startLive = async () => {
  operating.value = true
  try {
    await startLiveApi()
    ElMessage.success('直播已开始')
    await loadRoomInfo()
  } catch (error) {
    console.error('开始直播失败:', error)
    ElMessage.error('开始直播失败')
  } finally {
    operating.value = false
  }
}

// 结束直播
const stopLive = async () => {
  operating.value = true
  try {
    await stopLiveApi()
    ElMessage.success('直播已结束')
    await loadRoomInfo()
  } catch (error) {
    console.error('结束直播失败:', error)
    ElMessage.error('结束直播失败')
  } finally {
    operating.value = false
  }
}

// 复制文本
const copyText = (text) => {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

// 查看直播间
const viewLiveRoom = () => {
  router.push(`/live/room/${room.value.room_id}`)
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 加载商品列表
const loadProducts = async () => {
  if (!room.value) return
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://127.0.0.1:8000/live/products/${room.value.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    const data = await response.json()
    
    if (data.success) {
      products.value = data.products
    }
  } catch (error) {
    console.error('加载商品失败:', error)
  }
}

// 显示添加商品对话框
const showAddProductDialog = () => {
  isEditingProduct.value = false
  productForm.value = {
    product_name: '',
    description: '',
    price: 0,
    original_price: null,
    stock: 0,
    product_image: '',
    purchase_link: '',
    sort_order: 0
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
    sort_order: product.sort_order
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
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:8000/live/products/add', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(productForm.value)
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success(isEditingProduct.value ? '商品修改成功' : '商品添加成功')
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

onMounted(() => {
  loadRoomInfo()
  // 加载商品列表
  setTimeout(() => {
    loadProducts()
  }, 1000)
})
</script>

<style scoped>
.my-live-room-page {
  min-height: 100vh;
  padding: 30px;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #5C3317;
  margin: 0 0 30px 0;
}

/* 创建直播间 */
.create-room-section {
  max-width: 600px;
  margin: 0 auto;
}

.create-card {
  background: rgba(255, 248, 235, 0.85);
  border: 2px solid rgba(255, 173, 96, 0.3);
  border-radius: 16px;
}

.create-card h2 {
  color: #5C3317;
  margin: 0 0 10px 0;
}

.hint-text {
  color: #8B5A2B;
  margin-bottom: 24px;
}

.create-form {
  margin-top: 20px;
}

/* 状态卡片 */
.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.status-card {
  background: rgba(255, 248, 235, 0.85);
  border: 2px solid rgba(255, 173, 96, 0.3);
  border-radius: 12px;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
  background: linear-gradient(135deg, #C19875 0%, #A0826D 100%);
}

.card-icon.live {
  background: linear-gradient(135deg, #FF5C8D 0%, #FF3366 100%);
  animation: pulse 2s infinite;
}

.card-icon.viewers {
  background: linear-gradient(135deg, #5CC4E8 0%, #3FA8D6 100%);
}

.card-icon.likes {
  background: linear-gradient(135deg, #FFD93D 0%, #FFC107 100%);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.card-label {
  font-size: 13px;
  color: #8B5A2B;
  margin-bottom: 4px;
}

.card-value {
  font-size: 24px;
  font-weight: 700;
  color: #5C3317;
}

/* 推流配置 */
.stream-config {
  background: rgba(255, 248, 235, 0.85);
  border: 2px solid rgba(255, 173, 96, 0.3);
  border-radius: 16px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item label {
  font-size: 14px;
  font-weight: 600;
  color: #8B5A2B;
}

.config-value {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 240, 220, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(255, 173, 96, 0.2);
}

.config-value span,
.config-value code {
  flex: 1;
  color: #5C3317;
  font-size: 14px;
  word-break: break-all;
}

.stream-key {
  font-family: monospace;
  font-size: 13px;
}

.push-url {
  font-family: monospace;
  font-size: 12px;
  background: rgba(255, 192, 128, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.usage-alert {
  margin-top: 20px;
  background: rgba(255, 240, 220, 0.5);
  border: 1px solid rgba(255, 173, 96, 0.3);
}

.usage-steps p {
  margin: 6px 0;
  color: #8B5A2B;
}

/* 控制按钮 */
.control-buttons {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.control-buttons .el-button {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  padding: 16px;
}

/* 直播间信息 */
.room-info-card {
  background: rgba(255, 248, 235, 0.85);
  border: 2px solid rgba(255, 173, 96, 0.3);
  border-radius: 16px;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 80px 20px;
  color: #8B5A2B;
}

.loading-state p {
  margin-top: 16px;
  font-size: 16px;
}

/* 商品管理样式 */
.products-manage-card {
  margin-top: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.no-products {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 15px;
}

.hint-text {
  color: #8B5A2B;
  font-size: 14px;
}
</style>
