<template>
  <div class="users-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名"
              style="width: 200px; margin-right: 10px;"
              clearable
              @clear="handleSearch"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch" />
              </template>
            </el-input>
          </div>
        </div>
      </template>
      
      <el-table :data="userList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用户名" width="150" />
        <el-table-column label="用户类型" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.is_admin" type="danger">管理员</el-tag>
            <el-tag v-else type="info">普通用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="统计" width="200">
          <template #default="{ row }">
            <div style="font-size: 12px; color: #666;">
              收藏: {{ row.collections_count || 0 }} | 评论: {{ row.comments_count || 0 }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="250">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_admin"
              type="primary"
              size="small"
              @click="handleSetAdmin(row)"
            >
              设为管理员
            </el-button>
            <el-button
              v-else
              type="warning"
              size="small"
              @click="handleRemoveAdmin(row)"
            >
              取消管理员
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDelete(row)"
              :disabled="row.is_admin"
            >
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
import { Search } from '@element-plus/icons-vue'
import { getUserList, updateUserPermission, deleteUser } from '../../apis/admin'

const loading = ref(false)
const userList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    
    const res = await getUserList(params)
    if (res.code === 200) {
      userList.value = res.data.users
      total.value = res.data.total
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

const handlePageChange = () => {
  loadUsers()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadUsers()
}

const handleSetAdmin = (row) => {
  ElMessageBox.confirm(`确定要将用户"${row.name}"设置为管理员吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await updateUserPermission(row.id, { is_admin: true })
      if (res.code === 200) {
        ElMessage.success('设置成功')
        loadUsers()
      }
    } catch (error) {
      console.error('设置失败:', error)
    }
  }).catch(() => {})
}

const handleRemoveAdmin = (row) => {
  ElMessageBox.confirm(`确定要取消用户"${row.name}"的管理员权限吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await updateUserPermission(row.id, { is_admin: false })
      if (res.code === 200) {
        ElMessage.success('取消成功')
        loadUsers()
      }
    } catch (error) {
      console.error('取消失败:', error)
    }
  }).catch(() => {})
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除用户"${row.name}"吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    try {
      const res = await deleteUser(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadUsers()
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-management {
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
