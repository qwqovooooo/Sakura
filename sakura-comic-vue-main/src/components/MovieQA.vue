<template>
  <div class="movie-qa-container">
    <el-card class="qa-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span style="font-size: 18px; font-weight: bold; color: #8B5A2B;">
            AI 智能问答
          </span>
          <el-tag size="small" type="warning">体验版</el-tag>
        </div>
      </template>

      <!-- 问答历史记录 -->
      <div class="qa-history" ref="qaHistory">
        <div v-if="qaList.length === 0" class="empty-hint">
          <div style="font-size: 36px; color: #FF9A3C;">✨</div>
          <p style="color: #8B5A2B; margin-top: 10px; font-weight: 500;">问我任何关于这部电影的问题</p>
        </div>

        <div v-for="(qa, index) in qaList" :key="index" class="qa-item">
          <!-- 用户问题 -->
          <div class="question-bubble">
            <el-avatar :size="32" style="background: linear-gradient(135deg, #FF9A3C 0%, #FF6B35 100%);">
              <span style="font-size: 16px;">我</span>
            </el-avatar>
            <div class="message-content user-question">
              {{ qa.question }}
            </div>
          </div>

          <!-- AI回答 -->
          <div class="answer-bubble">
            <el-avatar :size="32" style="background: linear-gradient(135deg, #67C23A 0%, #85CE61 100%);">
              <span style="font-size: 14px;">AI</span>
            </el-avatar>
            <div class="message-content ai-answer">
              <div v-if="qa.loading" class="loading-dots">
                <span></span><span></span><span></span>
              </div>
              <div v-else>{{ qa.answer }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 建议问题 -->
      <div class="suggestions" v-if="qaList.length === 0">
        <p style="font-size: 14px; color: #999; margin-bottom: 10px;">试试这些问题：</p>
        <el-space wrap>
          <el-tag
            v-for="(suggestion, index) in suggestions"
            :key="index"
            type="info"
            effect="plain"
            @click="askSuggestion(suggestion)"
            class="suggestion-tag"
          >
            {{ suggestion }}
          </el-tag>
        </el-space>
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <el-input
          v-model="currentQuestion"
          placeholder="输入你的问题..."
          @keyup.enter="sendQuestion"
          :disabled="loading"
          clearable
        >
          <template #append>
            <el-button
              type="primary"
              @click="sendQuestion"
              :loading="loading"
              :disabled="!currentQuestion.trim()"
            >
              发送
            </el-button>
          </template>
        </el-input>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import httpRequest from '../request/index'

export default {
  name: 'MovieQA',
  props: {
    vod_id: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const qaList = ref([])
    const currentQuestion = ref('')
    const loading = ref(false)
    const qaHistory = ref(null)
    
    const suggestions = ref([
      '这部电影的主演是谁？',
      '导演是谁？',
      '这部电影讲什么？',
      '评分怎么样？',
      '是哪一年的作品？'
    ])

    // 滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (qaHistory.value) {
          qaHistory.value.scrollTop = qaHistory.value.scrollHeight
        }
      })
    }

    // 发送问题
    const sendQuestion = async () => {
      if (!currentQuestion.value.trim()) {
        return
      }

      const question = currentQuestion.value.trim()
      
      // 添加问题到列表
      const qaItem = {
        question: question,
        answer: '',
        loading: true
      }
      qaList.value.push(qaItem)
      currentQuestion.value = ''
      scrollToBottom()

      // 调用后端API
      loading.value = true
      try {
        const response = await httpRequest({
          url: '/movie-qa/ask',
          method: 'post',
          data: {
            vod_id: parseInt(props.vod_id),
            question: question
          }
        })

        if (response && response.success) {
          qaItem.answer = response.answer
        } else {
          qaItem.answer = response.error || '抱歉，回答失败了，请稍后再试'
        }
      } catch (error) {
        console.error('问答失败:', error)
        qaItem.answer = '抱歉，网络错误，请稍后再试'
      } finally {
        qaItem.loading = false
        loading.value = false
        scrollToBottom()
      }
    }

    // 点击建议问题
    const askSuggestion = (suggestion) => {
      currentQuestion.value = suggestion
      sendQuestion()
    }

    // 监听vod_id变化，清空问答记录
    watch(() => props.vod_id, () => {
      qaList.value = []
    })

    return {
      qaList,
      currentQuestion,
      loading,
      suggestions,
      qaHistory,
      sendQuestion,
      askSuggestion
    }
  }
}
</script>

<style scoped>
.movie-qa-container {
  margin: 20px 0;
  width: 90%;
}

.qa-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.qa-history {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 15px;
}

.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.qa-item {
  margin-bottom: 20px;
}

.question-bubble,
.answer-bubble {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  animation: fadeIn 0.3s ease-in;
}

.question-bubble {
  justify-content: flex-end;
}

.answer-bubble {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-wrap: break-word;
}

.user-question {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-answer {
  background-color: #f5f7fa;
  color: #333;
  border-bottom-left-radius: 4px;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.suggestions {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.suggestion-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.input-area {
  margin-top: 10px;
}

/* 滚动条样式 */
.qa-history::-webkit-scrollbar {
  width: 6px;
}

.qa-history::-webkit-scrollbar-thumb {
  background-color: #d9d9d9;
  border-radius: 3px;
}

.qa-history::-webkit-scrollbar-thumb:hover {
  background-color: #b3b3b3;
}
</style>
