<template>
  <div class="smart-search-page">
    <div class="search-container">
      <!-- 头部标题 -->
      <div class="header">
        <div class="header-icon-wrapper">
          <div class="header-icon">🎬</div>
          <div class="sparkles">
            <span class="sparkle">✨</span>
            <span class="sparkle">✨</span>
            <span class="sparkle">✨</span>
          </div>
        </div>
        <h1 class="gradient-text">智能电影推荐</h1>
        <p class="subtitle">告诉我你想看什么类型的电影，AI 帮你找到最合适的 💖</p>
      </div>

      <!-- 功能切换 -->
      <div class="mode-switcher">
        <el-segmented v-model="searchMode" :options="modeOptions" size="large" />
      </div>

      <!-- 搜索框 -->
      <div class="search-box">
        <el-input
          v-model="question"
          type="textarea"
          :rows="3"
          :placeholder="searchMode === 'recommend' ? '例如：我想看一些轻松搞笑的电影，适合周末放松' : '例如：查询评分最高的5部电影'"
          @keyup.ctrl.enter="handleSearch"
        />
        <div class="button-group">
          <el-button type="primary" @click="handleSearch" :loading="loading" size="large">
            {{ searchMode === 'recommend' ? '智能推荐' : '智能搜索' }}
          </el-button>
          <el-button @click="clearResult" size="large">
            清空
          </el-button>
        </div>
        <div class="hint">提示：按 Ctrl + Enter 快速搜索</div>
      </div>

      <!-- 示例问题 -->
      <div class="examples">
        <h3>💡 {{ searchMode === 'recommend' ? '试试这些描述：' : '试试这些问题：' }}</h3>
        <div class="example-tags">
          <el-tag
            v-for="(example, index) in currentExamples"
            :key="index"
            @click="fillQuestion(example)"
            class="example-tag"
            size="large"
            :type="index % 4 === 0 ? 'primary' : index % 4 === 1 ? 'success' : index % 4 === 2 ? 'warning' : 'danger'"
            effect="plain"
          >
            {{ example }}
          </el-tag>
        </div>
      </div>

      <!-- 结果展示 -->
      <div v-if="showResult" class="result-section">
        <!-- 推荐模式结果 -->
        <div v-if="searchMode === 'recommend' && result.success">
          <!-- 需求分析 -->
          <el-alert
            v-if="result.analysis"
            :title="'🧠 需求分析：' + result.analysis"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          />
          
          <!-- 查询策略 -->
          <el-alert
            v-if="result.query_strategy"
            :title="'⚙️ 查询策略：' + result.query_strategy"
            type="success"
            :closable="false"
            style="margin-bottom: 20px;"
          />
          
          <!-- SQL语句 -->
          <el-card v-if="result.sql" class="sql-card" style="margin-bottom: 20px;">
            <template #header>
              <div class="card-header">
                <span>📋 生成的SQL语句</span>
                <el-button size="small" @click="copySql">复制</el-button>
              </div>
            </template>
            <pre class="sql-code">{{ result.sql }}</pre>
          </el-card>
          
          <!-- 调试信息 -->
          <div v-if="result.movies" style="margin-bottom: 10px; color: #8B5A2B;">
            🎬 找到 {{ result.movies.length }} 部电影
          </div>
          
          <!-- 电影推荐卡片 -->
          <div v-if="result.movies && result.movies.length > 0" class="recommendation-grid">
            <el-card
              v-for="movie in result.movies"
              :key="movie.vod_id"
              class="recommendation-card"
              @click="handleMovieCardClick(movie)"
              shadow="hover"
            >
              <div class="rec-movie-poster">
                <img v-if="movie.vod_pic" :src="movie.vod_pic" :alt="movie.vod_name" />
                <div v-else class="rec-poster-placeholder">🎬</div>
              </div>
              <div class="rec-movie-info">
                <h3 class="rec-movie-title">{{ movie.vod_name }}</h3>
                <div class="rec-movie-meta">
                  <span v-if="movie.vod_score" class="rec-score">⭐ {{ movie.vod_score }}</span>
                  <span v-if="movie.vod_year" class="rec-year">📅 {{ movie.vod_year }}</span>
                </div>
                <div v-if="movie.vod_class" class="rec-tags">
                  <el-tag size="small" type="warning">{{ movie.vod_class }}</el-tag>
                </div>
                <div v-if="movie.reason" class="rec-reason">
                  <span class="reason-label">🎯 推荐理由：</span>
                  <span class="reason-text">{{ movie.reason }}</span>
                </div>
              </div>
            </el-card>
          </div>
          
          <el-empty 
            v-else 
            description="暂未找到合适的电影，请尝试换个描述😢" 
            :image-size="200"
          >
            <template #image>
              <div style="font-size: 5em;">🎬</div>
            </template>
            <template #description>
              <p style="color: #8B5A2B; font-size: 1.1em; margin-top: 10px;">
                暂未找到合适的电影，试试：
              </p>
              <ul style="color: #FF6B35; text-align: left; display: inline-block; margin-top: 10px;">
                <li>更换关键词（如：“喜剧”改为“搞笑”）</li>
                <li>添加更多细节（如：演员、导演、年份）</li>
                <li>切换到 SQL搜索模式试试</li>
              </ul>
            </template>
          </el-empty>
        </div>
        
        <!-- SQL搜索模式结果（原有的） -->
        <div v-else-if="searchMode === 'sql'">
          <!-- 统计信息 -->
          <div v-if="result.success" class="stats">
            <el-card class="stat-card stat-card-1">
              <div class="stat-icon">📊</div>
              <div class="stat-label">结果数量</div>
              <div class="stat-value">{{ resultCount }}</div>
            </el-card>
            <el-card class="stat-card stat-card-2">
              <div class="stat-icon">⚡</div>
              <div class="stat-label">查询时间</div>
              <div class="stat-value">{{ queryTime }}ms</div>
            </el-card>
            <el-card class="stat-card stat-card-3" v-if="isMovieQuery">
              <div class="stat-icon">🎬</div>
              <div class="stat-label">影片数据</div>
              <div class="stat-value">点击查看</div>
            </el-card>
          </div>

          <!-- 查询说明 -->
          <el-alert
            v-if="result.explanation"
            :title="result.explanation"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <!-- SQL语句 -->
          <el-card v-if="result.sql" class="sql-card">
            <template #header>
              <div class="card-header">
                <span>生成的SQL语句</span>
                <el-button size="small" @click="copySql">复制</el-button>
              </div>
            </template>
            <pre class="sql-code">{{ result.sql }}</pre>
          </el-card>

          <!-- 结果表格 -->
          <el-card v-if="result.success && result.result && result.result.length > 0" class="result-card">
            <template #header>
              <span>查询结果</span>
            </template>
            
            <!-- 如果是影片数据，显示卡片 -->
            <div v-if="isMovieQuery" class="movie-grid">
              <el-card 
                v-for="(movie, index) in result.result" 
                :key="index" 
                class="movie-card"
                @click="handleMovieCardClick(movie)"
                shadow="hover"
              >
                <div class="movie-card-content">
                  <div v-if="movie.vod_pic" class="movie-poster">
                    <img :src="movie.vod_pic" :alt="movie.vod_name" />
                  </div>
                  <div v-else class="movie-poster-placeholder">
                    <div class="placeholder-icon">🎬</div>
                  </div>
                  <div class="movie-info">
                    <h3 class="movie-title">{{ movie.vod_name || '未知影片' }}</h3>
                    <div class="movie-meta">
                      <span v-if="movie.vod_score" class="movie-score">⭐ {{ movie.vod_score }}</span>
                      <span v-if="movie.vod_remarks" class="movie-remarks">{{ movie.vod_remarks }}</span>
                    </div>
                    <div v-if="movie.vod_class" class="movie-tags">
                      <el-tag size="small" type="info">{{ movie.vod_class }}</el-tag>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>
            
            <!-- 如果不是影片数据，显示表格 -->
            <el-table
              v-else
              :data="result.result"
              stripe
              style="width: 100%"
              max-height="500"
            >
              <el-table-column
                v-for="(value, key) in result.result[0]"
                :key="key"
                :prop="key"
                :label="key"
                :show-overflow-tooltip="true"
              />
            </el-table>
          </el-card>

          <!-- 无结果提示 -->
          <el-empty
            v-if="result.success && (!result.result || result.result.length === 0)"
            description="暂无数据"
          />
        </div>

        <!-- 错误提示 -->
        <el-alert
          v-if="!result.success"
          :title="result.error || '查询失败'"
          type="error"
          :closable="false"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

// 直接创建 axios 实例，确保使用正确的后端地址
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 60000,  // 增加到60秒
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  name: 'SmartSearch',
  setup() {
    const router = useRouter()
    const question = ref('')
    const loading = ref(false)
    const showResult = ref(false)
    const result = ref({})
    const queryTime = ref(0)
    const startTime = ref(0)
    
    // 搜索模式：recommend(推荐) 或 sql(搜索)
    const searchMode = ref('recommend')
    const modeOptions = [
      { label: '🎬 智能推荐', value: 'recommend' },
      { label: '🔍 SQL搜索', value: 'sql' }
    ]

    // 推荐模式示例
    const recommendExamples = [
      '我想看一些轻松搞笑的电影，适合周末放松',
      '推荐几部高分悬疑片，最好是欧美的',
      '想看周星驰的喜剧电影',
      '有什么感人的爱情电影吗？',
      '推荐一些科幻大片，特效要好',
      '最近有哪些好看的国产动漫？',
      '想找一些烧脑的悬疑电影',
      '推荐经典老片，90年代的'
    ]
    
    // SQL搜索模式示例
    const sqlExamples = [
      '查询评分最高的5部电影',
      '最新的10部电影',
      '点击量最高的电影',
      '用户总数是多少',
      '统计各类型影片数量',
      '最新的20条评论',
      '2023年的电影',
      '查询动漫类型的作品'
    ]
    
    // 当前示例（根据模式切换）
    const currentExamples = computed(() => {
      return searchMode.value === 'recommend' ? recommendExamples : sqlExamples
    })

    const resultCount = computed(() => {
      if (searchMode.value === 'recommend') {
        return result.value.movies ? result.value.movies.length : 0
      }
      return result.value.result ? result.value.result.length : 0
    })

    const hasVodId = computed(() => {
      if (result.value.result && result.value.result.length > 0) {
        return 'vod_id' in result.value.result[0]
      }
      return false
    })

    const isMovieQuery = computed(() => {
      if (!hasVodId.value) return false
      
      const q = question.value.toLowerCase()
      const movieKeywords = ['电影', '影片', '视频', '动漫', '电视剧', '综艺', 'movie', 'vod', '评分', '点击', '最新', '热门']
      return movieKeywords.some(keyword => q.includes(keyword))
    })

    const fillQuestion = (text) => {
      question.value = text
    }

    const handleSearch = async () => {
      if (!question.value.trim()) {
        ElMessage.warning('请输入问题或描述')
        return
      }

      loading.value = true
      showResult.value = false
      startTime.value = Date.now()

      try {
        let response
        
        console.log('当前请求模式:', searchMode.value)
        console.log('API基础地址:', apiClient.defaults.baseURL)
        
        if (searchMode.value === 'recommend') {
          // 智能推荐模式
          console.log('发送推荐请求到: /recommend/recommend')
          const res = await apiClient.post('/recommend/recommend', {
            description: question.value,
            limit: 12
          })
          response = res.data
        } else {
          // SQL搜索模式
          const res = await apiClient.post('/sql-agent/ask', {
            question: question.value
          })
          response = res.data
        }

        queryTime.value = Date.now() - startTime.value
        result.value = response
        showResult.value = true
        
        // 调试日志
        console.log('=== 推荐结果 ===', response)
        if (searchMode.value === 'recommend') {
          console.log('电影数量:', response.movies ? response.movies.length : 0)
          console.log('电影数据:', response.movies)
        }

        if (response.success) {
          ElMessage.success(
            searchMode.value === 'recommend' ? '推荐成功' : '查询成功'
          )
        } else {
          ElMessage.error(response.error || '操作失败')
        }
      } catch (error) {
        console.error('查询错误:', error)
        ElMessage.error('网络错误，请确保后端服务已启动')
        result.value = {
          success: false,
          error: `网络错误: ${error.message || '未知错误'}`
        }
        showResult.value = true
      } finally {
        loading.value = false
      }
    }

    const clearResult = () => {
      question.value = ''
      showResult.value = false
      result.value = {}
    }

    const copySql = () => {
      if (result.value.sql) {
        navigator.clipboard.writeText(result.value.sql)
        ElMessage.success('SQL已复制到剪贴板')
      }
    }

    const handleRowClick = (row) => {
      if (isMovieQuery.value && row.vod_id) {
        router.push(`/movdetail/${row.vod_id}`)
      }
    }

    const handleMovieCardClick = (movie) => {
      if (movie.vod_id) {
        router.push(`/movdetail/${movie.vod_id}`)
      }
    }

    return {
      question,
      loading,
      showResult,
      result,
      queryTime,
      searchMode,
      modeOptions,
      currentExamples,
      resultCount,
      hasVodId,
      isMovieQuery,
      fillQuestion,
      handleSearch,
      clearResult,
      copySql,
      handleRowClick,
      handleMovieCardClick
    }
  }
}
</script>

<style scoped>
.smart-search-page {
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #FFF5E6 0%, #FFE4CC 50%, #FFD4B3 100%);
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}

.smart-search-page::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 154, 60, 0.1) 0%, transparent 70%);
  animation: float 20s infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -30px) rotate(120deg); }
  66% { transform: translate(-20px, 20px) rotate(240deg); }
}

.search-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header-icon-wrapper {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.header-icon {
  font-size: 5em;
  display: inline-block;
  animation: bounce 2s infinite;
  filter: drop-shadow(0 8px 16px rgba(255, 107, 53, 0.3));
}

@keyframes bounce {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-20px) rotate(-5deg); }
  50% { transform: translateY(0) rotate(0deg); }
  75% { transform: translateY(-10px) rotate(5deg); }
}

.sparkles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.sparkle {
  position: absolute;
  font-size: 1.5em;
  animation: sparkle 3s infinite;
}

.sparkle:nth-child(1) {
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.sparkle:nth-child(2) {
  top: 20%;
  right: 15%;
  animation-delay: 1s;
}

.sparkle:nth-child(3) {
  bottom: 15%;
  left: 20%;
  animation-delay: 2s;
}

@keyframes sparkle {
  0%, 100% { 
    opacity: 0;
    transform: scale(0) rotate(0deg);
  }
  50% { 
    opacity: 1;
    transform: scale(1.2) rotate(180deg);
  }
}

.gradient-text {
  font-size: 3.5em;
  font-weight: bold;
  margin-bottom: 15px;
  background: linear-gradient(135deg, #FF6B35 0%, #FF9A3C 50%, #FFB84D 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 12px rgba(255, 107, 53, 0.2);
  animation: gradientShift 5s infinite;
}

@keyframes gradientShift {
  0%, 100% { filter: hue-rotate(0deg); }
  50% { filter: hue-rotate(10deg); }
}

.subtitle {
  font-size: 1.3em;
  color: #8B5A2B;
  font-weight: 500;
  text-shadow: 0 2px 4px rgba(255, 255, 255, 0.5);
}

/* 模式切换 */
.mode-switcher {
  display: flex;
  justify-content: center;
  margin-bottom: 35px;
}

.mode-switcher :deep(.el-segmented) {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  padding: 6px;
  box-shadow: 0 8px 24px rgba(139, 90, 43, 0.15);
  border: 2px solid rgba(255, 154, 60, 0.2);
}

.mode-switcher :deep(.el-segmented__item) {
  color: #8B5A2B;
  font-weight: bold;
  padding: 14px 35px;
  font-size: 1.05em;
  transition: all 0.3s;
}

.mode-switcher :deep(.el-segmented__item:hover) {
  color: #FF6B35;
}

.mode-switcher :deep(.el-segmented__item.is-selected) {
  background: linear-gradient(135deg, #FF6B35 0%, #FF9A3C 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
  transform: scale(1.05);
}

.search-box {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 35px;
  box-shadow: 0 12px 40px rgba(139, 90, 43, 0.15);
  margin-bottom: 30px;
  transition: all 0.3s;
  border: 3px solid rgba(255, 154, 60, 0.2);
  backdrop-filter: blur(10px);
}

.search-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 50px rgba(255, 107, 53, 0.25);
  border-color: rgba(255, 107, 53, 0.4);
}

.search-box :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 2px solid rgba(255, 154, 60, 0.3);
  font-size: 1.1em;
  transition: all 0.3s;
  background: rgba(255, 248, 235, 0.5);
  color: #5C3317;
}

.search-box :deep(.el-textarea__inner):focus {
  border-color: #FF6B35;
  background: white;
  box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1);
}

.search-box :deep(.el-textarea__inner)::placeholder {
  color: rgba(139, 90, 43, 0.5);
}

.button-group {
  margin-top: 20px;
  display: flex;
  gap: 15px;
}

.button-group .el-button {
  border-radius: 14px;
  font-weight: bold;
  font-size: 1.05em;
  padding: 14px 32px;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.button-group .el-button--primary {
  background: linear-gradient(135deg, #FF6B35 0%, #FF9A3C 100%);
  border: none;
  box-shadow: 0 6px 20px rgba(255, 107, 53, 0.3);
}

.button-group .el-button--primary:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 30px rgba(255, 107, 53, 0.5);
}

.button-group .el-button--default {
  background: white;
  color: #FF6B35;
  border-color: rgba(255, 107, 53, 0.3);
}

.button-group .el-button--default:hover {
  background: rgba(255, 107, 53, 0.1);
  border-color: #FF6B35;
  transform: translateY(-2px);
}

.hint {
  margin-top: 12px;
  color: #8B5A2B;
  font-size: 0.9em;
  opacity: 0.8;
}

.examples {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 12px 40px rgba(139, 90, 43, 0.15);
  margin-bottom: 35px;
  border: 3px solid rgba(255, 154, 60, 0.2);
  backdrop-filter: blur(10px);
}

.examples h3 {
  margin-bottom: 18px;
  color: #5C3317;
  font-size: 1.2em;
  font-weight: bold;
}

.example-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.example-tag {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 20px;
  padding: 10px 18px;
  font-size: 0.95em;
  border: 2px solid transparent;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.example-tag:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 6px 16px rgba(255, 107, 53, 0.3);
}

.example-tag.el-tag--primary {
  background: linear-gradient(135deg, #FF6B35, #FF9A3C);
  border-color: transparent;
  color: white;
}

.example-tag.el-tag--success {
  background: linear-gradient(135deg, #FF9A3C, #FFB84D);
  border-color: transparent;
  color: #5C3317;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.3);
}

.example-tag.el-tag--warning {
  background: linear-gradient(135deg, #FFB84D, #FFC966);
  border-color: transparent;
  color: #5C3317;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.3);
}

.example-tag.el-tag--danger {
  background: linear-gradient(135deg, #FF8563, #FF6B35);
  border-color: transparent;
  color: white;
}

.result-section {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  text-align: center;
  color: white;
  border: none;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-card-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card-2 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card-3 {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-icon {
  font-size: 2.5em;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 0.9em;
  opacity: 0.9;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 2em;
  font-weight: bold;
}

.sql-card {
  margin-bottom: 20px;
  border-radius: 15px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #667eea;
}

.sql-code {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
  border-left: 4px solid #667eea;
}

.result-card {
  margin-bottom: 20px;
  border-radius: 15px;
  overflow: hidden;
}

.result-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
}

.result-card :deep(.el-table) {
  border-radius: 10px;
}

.result-card :deep(.el-table th) {
  background: #f5f7fa;
  color: #667eea;
  font-weight: bold;
}

.clickable-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.clickable-row:hover {
  background-color: #f0f9ff !important;
}

/* 影片卡片网格布局 */
.movie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  padding: 10px;
}

.movie-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 12px;
  overflow: hidden;
}

.movie-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(102, 126, 234, 0.3);
}

.movie-card-content {
  display: flex;
  flex-direction: column;
}

.movie-poster {
  width: 100%;
  height: 320px;
  overflow: hidden;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-bottom: 12px;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movie-poster-placeholder {
  width: 100%;
  height: 320px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  margin-bottom: 12px;
}

.placeholder-icon {
  font-size: 5em;
  opacity: 0.5;
}

.movie-info {
  padding: 5px;
}

.movie-title {
  font-size: 1.1em;
  font-weight: bold;
  color: #333;
  margin: 0 0 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  gap: 10px;
}

.movie-score {
  color: #f39c12;
  font-weight: bold;
  font-size: 0.95em;
}

.movie-remarks {
  color: #999;
  font-size: 0.9em;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.movie-tags {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

/* 推荐模式结果样式 */
.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 28px;
  padding: 25px;
}

.recommendation-card {
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 20px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.98);
  border: 3px solid rgba(255, 154, 60, 0.15);
  box-shadow: 0 8px 24px rgba(139, 90, 43, 0.12);
  position: relative;
}

.recommendation-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(255, 154, 60, 0.05) 100%);
  opacity: 0;
  transition: opacity 0.4s;
  z-index: 0;
}

.recommendation-card:hover {
  transform: translateY(-12px) scale(1.03);
  box-shadow: 0 20px 45px rgba(255, 107, 53, 0.35);
  border-color: rgba(255, 107, 53, 0.5);
}

.recommendation-card:hover::before {
  opacity: 1;
}

.rec-movie-poster {
  width: 100%;
  height: 400px;
  overflow: hidden;
  background: linear-gradient(135deg, #FFE5CC 0%, #FFD4B3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.rec-movie-poster::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(to top, rgba(0,0,0,0.3), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.recommendation-card:hover .rec-movie-poster::after {
  opacity: 1;
}

.rec-movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.recommendation-card:hover .rec-movie-poster img {
  transform: scale(1.15);
}

.rec-poster-placeholder {
  font-size: 7em;
  color: rgba(139, 90, 43, 0.25);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
}

.rec-movie-info {
  padding: 24px;
  position: relative;
  z-index: 1;
}

.rec-movie-title {
  font-size: 1.25em;
  font-weight: bold;
  color: #5C3317;
  margin: 0 0 14px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 2.5em;
  line-height: 1.25;
}

.rec-movie-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  gap: 12px;
}

.rec-score {
  color: #FF6B35;
  font-weight: bold;
  font-size: 1.05em;
  background: linear-gradient(135deg, rgba(255, 107, 53, 0.15), rgba(255, 154, 60, 0.15));
  padding: 6px 14px;
  border-radius: 20px;
  border: 2px solid rgba(255, 107, 53, 0.2);
  display: flex;
  align-items: center;
  gap: 4px;
}

.rec-year {
  color: #8B5A2B;
  font-size: 0.95em;
  background: rgba(139, 90, 43, 0.1);
  padding: 6px 14px;
  border-radius: 20px;
  border: 2px solid rgba(139, 90, 43, 0.15);
}

.rec-tags {
  margin-bottom: 14px;
}

.rec-tags .el-tag {
  border-radius: 12px;
  padding: 6px 14px;
  border: 2px solid rgba(255, 154, 60, 0.2);
}

.rec-reason {
  background: linear-gradient(135deg, rgba(255, 154, 60, 0.08) 0%, rgba(255, 107, 53, 0.08) 100%);
  padding: 14px;
  border-radius: 12px;
  border-left: 4px solid #FF6B35;
  position: relative;
  overflow: hidden;
}

.rec-reason::before {
  content: '🎯';
  position: absolute;
  right: 10px;
  bottom: 10px;
  font-size: 3em;
  opacity: 0.1;
}

.reason-label {
  font-weight: bold;
  color: #FF6B35;
  display: block;
  margin-bottom: 8px;
  font-size: 0.9em;
}

.reason-text {
  color: #5C3317;
  font-size: 0.95em;
  line-height: 1.6;
  display: block;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 2em;
  }
  
  .stats {
    flex-direction: column;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .movie-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
  
  .movie-poster,
  .movie-poster-placeholder {
    height: 220px;
  }
}
</style>
