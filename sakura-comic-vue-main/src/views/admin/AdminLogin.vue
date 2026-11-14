<template>
  <div class="admin-login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>USC20234080407罗靓管理后台</h2>
        <p>欢迎回来，管理员</p>
      </div>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
        <el-form-item prop="name">
          <el-input
            v-model="loginForm.name"
            placeholder="请输入管理员账号"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="login-btn"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-tips">
        <p>💡 默认管理员账号：admin / admin123</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAdminStore } from '../../store/admin'
import { adminLogin } from '../../apis/admin'

const router = useRouter()
const adminStore = useAdminStore()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  name: '',
  password: ''
})

const rules = {
  name: [
    { required: true, message: '请输入管理员账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const res = await adminLogin(loginForm)
        
        console.log('登录响应:', res) // 调试信息
        
        // 后端返回的数据结构是 { data: { code: 200, token: 'jwt xxx' } }
        if (res.data && res.data.code === 200 && res.data.token) {
          // 保存 token 和用户信息
          adminStore.setAdminToken(res.data.token)
          adminStore.setAdminInfo({
            name: loginForm.name,
            is_admin: true
          })
          
          ElMessage.success('登录成功！')
          
          // 跳转到管理后台
          setTimeout(() => {
            router.push('/admin/dashboard')
          }, 500)
        } else {
          ElMessage.error(res.data?.message || '登录失败')
        }
      } catch (error) {
        console.error('登录错误:', error)
        const errorMsg = error.response?.data?.detail?.data?.message || '登录失败，请检查账号密码'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.admin-login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.login-btn {
  width: 100%;
}

.login-tips {
  margin-top: 20px;
  text-align: center;
}

.login-tips p {
  font-size: 12px;
  color: #999;
}
</style>
