<template>
  <div class="login-container">
    <div class="tech-container-bg"></div>

    <div class="notice-box">
      <!-- 装饰角落 -->
      <div class="corner-top-left"></div>
      <div class="corner-top-right"></div>
      <div class="corner-bottom-left"></div>
      <div class="corner-bottom-right"></div>

      <!-- 图标 -->
      <div class="notice-icon">
        <el-icon><Lock /></el-icon>
      </div>

      <!-- 标题 -->
      <h1 class="notice-title">科研情报系统</h1>
      <p class="notice-subtitle">Scientific Research Intelligence System</p>

      <!-- 提示信息 -->
      <div class="notice-content">
        <div class="notice-tip">
          <el-icon class="tip-icon"><WarningFilled /></el-icon>
          <span>本系统仅支持通过统一登录入口访问</span>
        </div>
        <p class="notice-desc">请通过以下地址登录后跳转进入本系统：</p>
        <a class="notice-link" href="https://10.68.16.92/" target="_self">
          <el-icon><Link /></el-icon>
          https://10.68.16.92/
        </a>
      </div>

      <!-- 底部 -->
      <div class="notice-footer">
        <p>&copy; {{ new Date().getFullYear() }} 科研情报系统</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Lock, WarningFilled, Link } from '@element-plus/icons-vue'
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100vw;
  background-color: #0b0f19;
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
  0%   { transform: scale(1)   translate(0, 0); }
  50%  { transform: scale(1.1) translate(30px, -30px); }
  100% { transform: scale(0.9) translate(-30px, 30px); }
}

/* 通知卡片 */
.notice-box {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 520px;
  padding: 60px 60px 40px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.01) 100%);
  border-radius: 36px;
  box-shadow:
    0 30px 60px rgba(0, 0, 0, 0.4),
    inset 0 1px 3px rgba(255, 255, 255, 0.2),
    inset 0 -1px 3px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(48px) saturate(180%);
  -webkit-backdrop-filter: blur(48px) saturate(180%);
  text-align: center;
}

.corner-top-left,
.corner-top-right,
.corner-bottom-left,
.corner-bottom-right {
  display: none;
}

/* 锁图标 */
.notice-icon {
  font-size: 56px;
  background: linear-gradient(135deg, #fff 0%, #a0cfff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 20px;
  filter: drop-shadow(0 8px 16px rgba(0, 195, 255, 0.4));
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-10px); }
}

.notice-title {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 8px;
  letter-spacing: 2px;
}

.notice-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin: 0 0 36px;
}

/* 提示内容区 --  */
.notice-content {
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 36px;
}

.notice-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #ffd666;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
}

.tip-icon {
  font-size: 18px;
  color: #ffd666;
}

.notice-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0 0 16px;
}

.notice-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #00e5ff;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  padding: 10px 22px;
  border: 1px solid rgba(0, 229, 255, 0.4);
  border-radius: 12px;
  background: rgba(0, 229, 255, 0.06);
  transition: all 0.3s ease;
  letter-spacing: 0.5px;
}

.notice-link:hover {
  background: rgba(0, 229, 255, 0.15);
  border-color: rgba(0, 229, 255, 0.7);
  box-shadow: 0 0 16px rgba(0, 229, 255, 0.25);
  transform: translateY(-2px);
}

.notice-footer p {
  color: rgba(255, 255, 255, 0.3);
  font-size: 13px;
  margin: 0;
  letter-spacing: 1px;
}

@media (max-width: 600px) {
  .notice-box {
    width: 90%;
    padding: 40px 28px 30px;
    border-radius: 24px;
  }
}
</style>