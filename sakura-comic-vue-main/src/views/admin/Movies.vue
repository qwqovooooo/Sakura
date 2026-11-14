<template>
  <div class="movies-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>视频管理</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索视频名称"
              style="width: 200px; margin-right: 10px;"
              clearable
              @clear="handleSearch"
            >
              <template #append>
                <el-button :icon="Search" @click="handleSearch" />
              </template>
            </el-input>
            <el-button type="primary" @click="showAddDialog">
              <el-icon><Plus /></el-icon>
              添加视频
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="movieList" v-loading="loading" stripe>
        <el-table-column prop="vod_id" label="ID" width="80" />
        <el-table-column prop="vod_name" label="电影名称" width="200" show-overflow-tooltip />
        <el-table-column prop="type_name" label="分类" width="100" />
        <el-table-column prop="vod_year" label="年份" width="80" />
        <el-table-column prop="vod_area" label="地区" width="80" />
        <el-table-column prop="vod_remarks" label="状态" width="100" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
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
    
    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="movieForm" label-width="100px">
        <el-form-item label="视频名称">
          <el-input v-model="movieForm.vod_name" placeholder="请输入视频名称" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="movieForm.type_name" placeholder="例如：动作、喜剧" />
        </el-form-item>
        <el-form-item label="年份">
          <el-input v-model="movieForm.vod_year" placeholder="例如：2024" />
        </el-form-item>
        <el-form-item label="地区">
          <el-input v-model="movieForm.vod_area" placeholder="例如：中国大陆" />
        </el-form-item>
        <el-form-item label="状态">
          <el-input v-model="movieForm.vod_remarks" placeholder="例如：更新至10集" />
        </el-form-item>
        <el-form-item label="演员">
          <el-input v-model="movieForm.vod_actor" placeholder="多个演员用逗号分隔" />
        </el-form-item>
        <el-form-item label="导演">
          <el-input v-model="movieForm.vod_director" placeholder="请输入导演" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input
            v-model="movieForm.vod_content"
            type="textarea"
            :rows="4"
            placeholder="请输入视频简介"
          />
        </el-form-item>
        <el-form-item label="封面图">
          <el-input v-model="movieForm.vod_pic" placeholder="请输入封面图URL" />
        </el-form-item>
        <el-form-item label="播放地址">
          <el-input v-model="movieForm.vod_play_url" placeholder="请输入播放地址URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getMovieList, createMovie, updateMovie, deleteMovie } from '../../apis/admin'

const loading = ref(false)
const movieList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')

const dialogVisible = ref(false)
const dialogTitle = ref('添加视频')
const submitting = ref(false)
const editingMovie = ref(null)

const movieForm = ref({
  vod_name: '',
  type_name: '',
  vod_year: '',
  vod_area: '',
  vod_remarks: '',
  vod_actor: '',
  vod_director: '',
  vod_content: '',
  vod_pic: '',
  vod_play_url: ''
})

const loadMovies = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    
    const res = await getMovieList(params)
    if (res.code === 200) {
      movieList.value = res.data.movies
      total.value = res.data.total
    }
  } catch (error) {
    console.error('加载视频列表失败:', error)
    ElMessage.error('加载视频列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadMovies()
}

const handlePageChange = () => {
  loadMovies()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadMovies()
}

const showAddDialog = () => {
  dialogTitle.value = '添加视频'
  editingMovie.value = null
  movieForm.value = {
    vod_name: '',
    type_name: '',
    vod_year: '',
    vod_area: '',
    vod_remarks: '',
    vod_actor: '',
    vod_director: '',
    vod_content: '',
    vod_pic: '',
    vod_play_url: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑视频'
  editingMovie.value = row
  movieForm.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!movieForm.value.vod_name) {
    ElMessage.warning('请输入视频名称')
    return
  }
  
  submitting.value = true
  try {
    let res
    if (editingMovie.value) {
      res = await updateMovie(editingMovie.value.vod_id, movieForm.value)
    } else {
      res = await createMovie(movieForm.value)
    }
    
    if (res.code === 200) {
      ElMessage.success(editingMovie.value ? '更新成功' : '添加成功')
      dialogVisible.value = false
      loadMovies()
    }
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除视频"${row.vod_name}"吗？此操作不可恢复！`, '警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'error'
  }).then(async () => {
    try {
      const res = await deleteMovie(row.vod_id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        loadMovies()
      }
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  loadMovies()
})
</script>

<style scoped>
.movies-management {
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
