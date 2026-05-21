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
  background-color: #0b0f19;
  /* Premium abstract background for liquid glass effect */
  background-image:
    radial-gradient(circle at 15% 50%, rgba(0, 195, 255, 0.25), transparent 50%),
    radial-gradient(circle at 85% 30%, rgba(0, 85, 255, 0.3), transparent 50%),
    radial-gradient(circle at 50% 80%, rgba(55, 0, 255, 0.2), transparent 50%),
    radial-gradient(ellipse at center, #050a1f 0%, #020513 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
  overflow: hidden;
  position: relative;
}

.tech-container-bg {
  /* Orbs for glass interaction */
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 20% 80%, rgba(0, 255, 200, 0.15) 0%, transparent 40%),
    radial-gradient(circle at 80% 20%, rgba(150, 0, 255, 0.15) 0%, transparent 40%);
  filter: blur(40px);
  animation: orbDrift 20s infinite alternate ease-in-out;
}

@keyframes orbDrift {
  0% {
    transform: scale(1) translate(0, 0);
  }

  50% {
    transform: scale(1.1) translate(30px, -30px);
  }

  100% {
    transform: scale(0.9) translate(-30px, 30px);
  }
}

.login-box {
  position: relative;
  z-index: 1;
  display: flex;
  width: 900px;
  height: 550px;
  /* Liquid glass core setup */
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.01) 100%);
  border-radius: 36px;
  box-shadow:
    0 30px 60px rgba(0, 0, 0, 0.4),
    inset 0 1px 3px rgba(255, 255, 255, 0.2),
    inset 0 -1px 3px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(48px) saturate(180%);
  -webkit-backdrop-filter: blur(48px) saturate(180%);
  transform-style: preserve-3d;
  perspective: 1000px;
}

/* Remove harsh tech corners */
.corner-top-left,
.corner-top-right,
.corner-bottom-left,
.corner-bottom-right {
  display: none;
}

.login-left {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  padding: 40px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.03), transparent);
  border-top-left-radius: 36px;
  border-bottom-left-radius: 36px;
}

.brand-info {
  text-align: center;
  z-index: 2;
}

.logo-placeholder {
  font-size: 64px;
  background: linear-gradient(135deg, #fff 0%, #a0cfff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 25px;
  filter: drop-shadow(0 10px 20px rgba(0, 195, 255, 0.4));
  animation: float 4s ease-in-out infinite;
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0px);
  }

  50% {
    transform: translateY(-12px);
  }
}

.brand-info h1 {
  font-size: 32px;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 10px;
  letter-spacing: 2px;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.brand-info p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 2px;
  text-transform: uppercase;
  font-weight: 500;
}

.tech-decoration {
  display: none;
  /* Hide old tech circles for modern glass UI */
}

.login-right {
  flex: 1;
  padding: 50px 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-header {
  margin-bottom: 35px;
}

.form-header h2 {
  font-size: 24px;
  color: #ffffff;
  margin: 0 0 8px;
  font-weight: 700;
  display: flex;
  align-items: center;
}

.form-header .highlight {
  background: linear-gradient(135deg, #00e5ff 0%, #005bb5 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 800;
  margin-left: 8px;
  font-size: 26px;
}

.form-header p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0;
}

/* Glassmorphism Forms */
.login-form :deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 600;
  font-size: 13px;
  padding-bottom: 8px;
}

.login-form :deep(.el-input__wrapper) {
  background-color: rgba(0, 0, 0, 0.15) !important;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3), inset 0 0 0 1px rgba(255, 255, 255, 0.05) !important;
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-form :deep(.el-input__wrapper.is-focus),
.login-form :deep(.el-input__wrapper:hover) {
  background-color: rgba(255, 255, 255, 0.05) !important;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1), inset 0 0 0 1px rgba(255, 255, 255, 0.3) !important;
}

.login-form :deep(.el-input__inner) {
  color: #ffffff !important;
  height: 48px;
  font-size: 15px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
}

.login-form :deep(.el-input__prefix-inner) {
  color: rgba(255, 255, 255, 0.6);
  font-size: 18px;
}

.login-form :deep(.el-input__suffix-inner) {
  color: rgba(255, 255, 255, 0.6);
}

.tech-btn {
  width: 100%;
  height: 52px;
  margin-top: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
  color: #ffffff;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(20px);
}

.tech-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 12px 25px rgba(0, 0, 0, 0.3), inset 0 1px 2px rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.tech-btn:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.btn-icon {
  margin-left: 10px;
  font-size: 18px;
  transition: transform 0.3s;
}

.tech-btn:hover .btn-icon {
  transform: translateX(4px);
}

.error-message {
  background-color: rgba(255, 77, 79, 0.15);
  border: 1px solid rgba(255, 77, 79, 0.4);
  border-radius: 12px;
  padding: 12px 15px;
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffaaaa;
  font-size: 13px;
  backdrop-filter: blur(10px);
}

.login-footer {
  margin-top: auto;
  text-align: center;
  padding-top: 20px;
}

.login-footer p {
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
  margin: 0;
  letter-spacing: 1px;
}

@media (max-width: 850px) {
  .login-box {
    width: 90%;
    height: auto;
    flex-direction: column;
    border-radius: 28px;
  }

  .login-left {
    padding: 40px 30px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    min-height: 200px;
    border-radius: 28px 28px 0 0;
  }

  .login-right {
    padding: 40px 30px;
  }
}
</style>