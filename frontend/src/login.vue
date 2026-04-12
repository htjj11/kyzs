<template>
  <div class="login-container">
    <!-- Starry/Tech Background -->
    <div class="tech-container-bg"></div>

    <div class="login-box">
      <!-- Decor Corners -->
      <div class="corner-top-left"></div>
      <div class="corner-top-right"></div>
      <div class="corner-bottom-left"></div>
      <div class="corner-bottom-right"></div>

      <!-- Left: Branding & Decoration -->
      <div class="login-left">
        <div class="brand-info">
          <div class="logo-placeholder">
            <el-icon>
              <Monitor />
            </el-icon>
          </div>
          <h1>科研情报系统</h1>
          <p>Scientific Research Intelligence System</p>
        </div>
        <div class="tech-decoration">
          <div class="circle-1"></div>
          <div class="circle-2"></div>
        </div>
      </div>

      <!-- Right: Login Form -->
      <div class="login-right">
        <div class="form-header">
          <h2>欢迎登录 / <span class="highlight">LOGIN</span></h2>
          <p>请输入您的账号信息进入系统</p>
        </div>

        <div class="login-form">
          <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-position="top">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" :prefix-icon="User" autocomplete="username" />
            </el-form-item>

            <el-form-item label="密码" prop="password">
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" :prefix-icon="Lock"
                show-password autocomplete="current-password" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" class="login-button tech-btn" :loading="isLoading" @click="handleLogin"
                :disabled="isLoading">
                <span>{{ isLoading ? '登录中...' : '登 录 系 统' }}</span>
                <el-icon class="btn-icon">
                  <ArrowRight />
                </el-icon>
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="errorMsg" class="error-message">
            <el-icon>
              <WarningFilled />
            </el-icon>
            {{ errorMsg }}
          </div>
        </div>

        <div class="login-footer">
          <p>&copy; {{ new Date().getFullYear() }} 科研情报系统 测试</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, WarningFilled, Monitor, ArrowRight } from '@element-plus/icons-vue'
import request from './api/request'
import { setUserIdCookie, setUserNameCookie, setExpireTimeCookie, setPermissionCookie } from './utils/authUtils'

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
      const permission = response.data.data.permission

      // 使用统一的authUtils中的函数设置cookie
      setUserIdCookie(userId, 30)
      // 设置user_name
      setUserNameCookie(userName)
      // 设置permission
      setPermissionCookie(permission, 30)

      // 设置单独的截止日期字段 (当前时间 + 30分钟的时间戳)
      const expireTimestamp = new Date().getTime() + 30 * 60 * 1000;
      setExpireTimeCookie(expireTimestamp, 30)

      ElMessage.success('登录成功')

      // 跳转至首页或指定页面
      setTimeout(() => {
        router.push('/literatureSearch')
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
    } else if (error.message && error.message.includes('Failed to validate form')) {
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
  background-color: #050a1f;
  /* Dark tech background */
  background-image:
    radial-gradient(ellipse at center, rgba(10, 25, 70, 0.8) 0%, rgba(5, 10, 31, 1) 100%),
    linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 100% 100%, 30px 30px, 30px 30px;
  background-position: center, center, center;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  overflow: hidden;
  position: relative;
}

.tech-container-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

.login-box {
  position: relative;
  z-index: 1;
  display: flex;
  width: 900px;
  height: 550px;
  background: rgba(13, 22, 53, 0.6);
  border-radius: 12px;
  box-shadow: 0 0 30px rgba(0, 195, 255, 0.15), inset 0 0 15px rgba(0, 195, 255, 0.1);
  border: 1px solid rgba(0, 195, 255, 0.3);
  backdrop-filter: blur(10px);
  animation: boxGlow 4s infinite alternate;
}

@keyframes boxGlow {
  0% {
    box-shadow: 0 0 30px rgba(0, 195, 255, 0.15), inset 0 0 15px rgba(0, 195, 255, 0.1);
  }

  100% {
    box-shadow: 0 0 50px rgba(0, 195, 255, 0.3), inset 0 0 25px rgba(0, 195, 255, 0.2);
  }
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, rgba(0, 195, 255, 0.1) 0%, rgba(13, 22, 53, 0) 100%);
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-right: 1px solid rgba(0, 195, 255, 0.2);
  padding: 40px;
  overflow: hidden;
}

.brand-info {
  text-align: center;
  z-index: 2;
}

.logo-placeholder {
  font-size: 64px;
  color: #00e5ff;
  margin-bottom: 20px;
  text-shadow: 0 0 20px rgba(0, 229, 255, 0.6);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }

  50% {
    transform: translateY(-10px);
  }

  100% {
    transform: translateY(0px);
  }
}

.brand-info h1 {
  font-size: 34px;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 10px;
  letter-spacing: 4px;
  text-shadow: 0 0 10px rgba(0, 195, 255, 0.5);
}

.brand-info p {
  font-size: 13px;
  color: #a0cfff;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.tech-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
  pointer-events: none;
}

.circle-1,
.circle-2 {
  position: absolute;
  border-radius: 50%;
  border: 1px dashed rgba(0, 195, 255, 0.3);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.circle-1 {
  width: 280px;
  height: 280px;
  animation: rotate 20s linear infinite;
}

.circle-2 {
  width: 380px;
  height: 380px;
  border-style: solid;
  border-width: 1px 0;
  border-color: rgba(0, 195, 255, 0.2);
  animation: rotate reverse 30s linear infinite;
}

@keyframes rotate {
  100% {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

.login-right {
  flex: 1;
  padding: 50px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: rgba(5, 10, 31, 0.4);
}

.form-header {
  margin-bottom: 30px;
}

.form-header h2 {
  font-size: 22px;
  color: #ffffff;
  margin: 0 0 8px;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.form-header .highlight {
  color: #00e5ff;
  font-weight: 800;
  margin-left: 8px;
  font-size: 26px;
}

.form-header p {
  color: #82a8d1;
  font-size: 13px;
  margin: 0;
}

/* Customizing Element Plus Form in Scoped */
.login-form :deep(.el-form-item__label) {
  color: #a0cfff;
  font-weight: 500;
}

.login-form :deep(.el-input__wrapper) {
  background-color: rgba(13, 22, 53, 0.5) !important;
  box-shadow: 0 0 0 1px rgba(0, 195, 255, 0.3) inset !important;
  border-radius: 4px;
}

.login-form :deep(.el-input__wrapper.is-focus),
.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #00e5ff inset, 0 0 8px rgba(0, 229, 255, 0.3) !important;
}

.login-form :deep(.el-input__inner) {
  color: #ffffff !important;
  height: 42px;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: #4a6b9c;
}

.login-form :deep(.el-input__prefix-inner),
.login-form :deep(.el-input__suffix-inner) {
  color: #00e5ff;
  font-size: 16px;
}

.tech-btn {
  width: 100%;
  height: 46px;
  background: linear-gradient(90deg, #005bb5 0%, #00e5ff 100%);
  border: none;
  border-radius: 4px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 2px;
  color: #ffffff;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s;
  margin-top: 15px;
}

.tech-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 229, 255, 0.4);
}

.tech-btn:active:not(:disabled) {
  transform: translateY(0);
}

.tech-btn::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: scan 3s infinite linear;
}

@keyframes scan {
  0% {
    left: -100%;
  }

  100% {
    left: 100%;
  }
}

.btn-icon {
  margin-left: 8px;
  font-size: 16px;
}

.error-message {
  background-color: rgba(255, 77, 79, 0.1);
  border: 1px solid rgba(255, 77, 79, 0.5);
  border-radius: 4px;
  padding: 10px 15px;
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ff4d4f;
  font-size: 13px;
}

.login-footer {
  margin-top: auto;
  text-align: center;
  padding-top: 20px;
}

.login-footer p {
  color: #4a6b9c;
  font-size: 12px;
  margin: 0;
}

/* 装饰线条 */
.corner-top-left,
.corner-top-right,
.corner-bottom-left,
.corner-bottom-right {
  position: absolute;
  width: 20px;
  height: 20px;
  border-color: #00e5ff;
  border-style: solid;
  z-index: 10;
}

.corner-top-left {
  top: -1px;
  left: -1px;
  border-width: 2px 0 0 2px;
  border-top-left-radius: 12px;
}

.corner-top-right {
  top: -1px;
  right: -1px;
  border-width: 2px 2px 0 0;
  border-top-right-radius: 12px;
}

.corner-bottom-left {
  bottom: -1px;
  left: -1px;
  border-width: 0 0 2px 2px;
  border-bottom-left-radius: 12px;
}

.corner-bottom-right {
  bottom: -1px;
  right: -1px;
  border-width: 0 2px 2px 0;
  border-bottom-right-radius: 12px;
}

@media (max-width: 850px) {
  .login-box {
    width: 90%;
    height: auto;
    flex-direction: column;
  }

  .login-left {
    padding: 30px;
    border-right: none;
    border-bottom: 1px solid rgba(0, 195, 255, 0.2);
    min-height: 200px;
  }

  .circle-1 {
    width: 160px;
    height: 160px;
  }

  .circle-2 {
    width: 220px;
    height: 220px;
  }

  .login-right {
    padding: 30px;
  }
}
</style>