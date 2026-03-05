<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-header">
        <h1 class="login-title">科研情报系统</h1>
        <p class="login-subtitle">请输入用户名和密码进行登录</p>
      </div>
      
      <div class="login-form">
        <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-position="left">
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名" 
              :prefix-icon="User" 
              autocomplete="username"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码" 
              :prefix-icon="Lock" 
              show-password 
              autocomplete="current-password"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              class="login-button" 
              :loading="isLoading" 
              @click="handleLogin"
              :disabled="isLoading"
            >
              {{ isLoading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <div v-if="errorMsg" class="error-message">
          <el-icon><WarningFilled /></el-icon>
          {{ errorMsg }}
        </div>
      </div>
      
      <div class="login-footer">
        <p>&copy; {{ new Date().getFullYear() }} 科研情报系统 测试</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, WarningFilled } from '@element-plus/icons-vue'
import request from './api/request'
import { setUserIdCookie, setUserNameCookie } from './utils/authUtils'

const router = useRouter()
const isLoading = ref(false)
const errorMsg = ref('')
const loginFormRef = ref(null)

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 1, max: 50, message: '用户名长度应为1-50个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 1, max: 50, message: '密码长度应为1-50个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  // 验证表单
  try {
    await loginFormRef.value.validate()
    
    // 清除之前的错误信息
    errorMsg.value = ''
    isLoading.value = true
    
    // 调用登录接口
    const response = await request.post('/system/login', {
      username: loginForm.username,
      password: loginForm.password
    })
    
    // 处理响应
    if (response.data && response.data.code === 200) {
      // 登录成功，获取用户ID
      const userId = response.data.data.user_id
      const userName = response.data.data.user_name
      
      // 使用统一的authUtils中的函数设置cookie
      setUserIdCookie(userId, 30)
      // 设置user_name
      setUserNameCookie(userName)

      
      ElMessage.success('登录成功')
      
      // 跳转至首页或指定页面
      setTimeout(() => {
        router.push('/wxjs')
      }, 1000)
      // 刷新页面
      setTimeout(() => {
        location.reload();
      }, 1000)

    } else {
      // 登录失败
      errorMsg.value = response.data?.msg || '登录失败，请重试'
    }
  } catch (error) {
    console.error('登录错误:', error)
    if (error.response) {
      // 服务器返回错误
      errorMsg.value = error.response.data?.msg || '用户名或密码错误'
    } else if (error.message.includes('Failed to validate form')) {
      // 表单验证失败，不显示错误信息
    } else {
      // 其他错误
      errorMsg.value = '登录失败，请检查网络连接'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.login-wrapper {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  width: 400px;
  max-width: 90%;
  overflow: hidden;
  transition: transform 0.3s ease;
}

.login-wrapper:hover {
  transform: translateY(-2px);
}

.login-header {
  padding: 32px 32px 24px;
  text-align: center;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
}

.login-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.login-subtitle {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.login-form {
  padding: 32px;
}

.el-form {
  margin-bottom: 0;
}

.el-form-item {
  margin-bottom: 24px;
}

.el-form-item__label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
  padding-bottom: 8px;
}

.el-input {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.el-input__wrapper {
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.el-input__wrapper:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.error-message {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 12px 16px;
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #b91c1c;
  font-size: 14px;
}

.error-message :deep(.el-icon) {
  color: #ef4444;
}

.login-footer {
  background: #f8fafc;
  padding: 20px 32px;
  text-align: center;
  border-top: 1px solid #e2e8f0;
}

.login-footer p {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-wrapper {
    width: 95%;
    border-radius: 12px;
  }
  
  .login-header {
    padding: 24px 24px 16px;
  }
  
  .login-title {
    font-size: 24px;
  }
  
  .login-form {
    padding: 24px;
  }
  
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .login-footer {
    padding: 16px 24px;
  }
}

/* 动画效果 */
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

.login-header,
.login-form,
.login-footer {
  animation: fadeIn 0.5s ease-out;
}

.login-header {
  animation-delay: 0.1s;
}

.login-form {
  animation-delay: 0.2s;
}

.login-footer {
  animation-delay: 0.3s;
}
</style>