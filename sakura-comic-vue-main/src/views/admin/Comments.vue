<template>
  <div class="comments-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>评论管理</span>
          <div class="header-actions">
            <el-button
              type="danger"
              :disabled="selectedComments.length === 0"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>
              批量删除 ({{ selectedComments.length }})
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="commentList"
        v-loading="loading"
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="movie_name" label="电影" width="200" show-overflow-tooltip />
        <el-table-column prop="content" label="评论内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="created_at" label="评论时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { getCommentList, deleteComment, batchDeleteComments } from '../../apis/admin'

const loading = ref(false)
const commentList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedComments = ref([])

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadComments = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const res = await getCommentList(params)
    if (res.code === 200) {
      commentList.value = res.data.comments
      total.value = res.data.total
    }
  } catch (error) {
    console.error('加载评论列表失败:', error)
    ElMessage.error('加载评论列表失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = () => {
  loadComments()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadComments()
}

const handleSelectionChange = (selection) => {
  selectedComments.value = selection
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除这条评论吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    try {
      const res = await deleteComment(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadComments()
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleBatchDelete = () => {
  ElMessageBox.confirm(`确定要删除选中的 ${selectedComments.value.length} 条评论吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    try {
      const commentIds = selectedComments.value.map(c => c.id)
      const res = await batchDeleteComments(commentIds)
      if (res.code === 200) {
        ElMessage.success(`成功删除 ${res.data.deleted_count} 条评论`)
        loadComments()
      }
    } catch (error) {
      console.error('批量删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  loadComments()
})
</script>

<style scoped>
.comments-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
