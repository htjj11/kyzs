<template>
  <!-- 条件渲染：如果未登录，只显示路由视图（登录页面） -->
  <div v-if="!isLoggedIn" class="login-container">
    <router-view></router-view>
  </div>

  <!-- 如果已登录，显示完整的应用布局 -->
  <div v-else class="research-layout">
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-content">
          <div class="header-left">
            <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
              <component :is="isCollapse ? 'Expand' : 'Fold'" />
            </el-icon>
            <h1 class="system-title">
              <el-icon class="title-icon">
                <Document />
              </el-icon>
              科研情报系统
            </h1>
          </div>
          <div class="header-actions">
            <span class="id-value">{{ currentUserName }}</span>

            <el-dropdown trigger="click">
              <div class="user-avatar-circle clickable">
                {{ userInitial }}
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="showAccountSettingModal = true">
                    <el-icon>
                      <Edit />
                    </el-icon> 个人设置
                  </el-dropdown-item>
                  <el-dropdown-item @click="showAboutModal = true">
                    <el-icon>
                      <InfoFilled />
                    </el-icon> 关于系统
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout" style="color: #f56c6c;">
                    <el-icon>
                      <SwitchButton />
                    </el-icon> 注销登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-container class="body-container">
        <!-- 侧边栏 -->
        <el-aside :class="['sidebar', { 'is-collapsed': isCollapse }]">
          <div class="sidebar-content">
            <el-menu :collapse="isCollapse" :collapse-transition="true" default-active="1" class="sidebar-menu"
              @open="handleOpen" @close="handleClose" background-color="transparent" text-color="#4a5568"
              active-text-color="#3b82f6">
              <el-sub-menu index="1" class="menu-group">
                <template #title>
                  <div class="menu-title">
                    <el-icon class="menu-icon">
                      <Location />
                    </el-icon>
                    <span>报告智能体</span>
                  </div>
                </template>
                <div class="submenu-group">
                  <div class="group-label">知识信息检索</div>
                  <el-menu-item index="/literatureSearch" class="menu-item">
                    <el-icon>
                      <Document />
                    </el-icon>
                    <router-link to="/literatureSearch" class="menu-link">文献检索</router-link>
                  </el-menu-item>
                  <el-menu-item index="/patentSearch" class="menu-item">
                    <el-icon>
                      <Collection />
                    </el-icon>
                    <router-link to="/patentSearch" class="menu-link">专利检索</router-link>
                  </el-menu-item>
                  <el-menu-item index="/webinfoSearch" class="menu-item">
                    <el-icon>
                      <Connection />
                    </el-icon>
                    <router-link to="/webinfoSearch" class="menu-link">网络信息检索</router-link>
                  </el-menu-item>

                </div>

                <div class="submenu-group">
                  <div class="group-label">报告智能体</div>
                  <el-menu-item index="6" class="menu-item">
                    <el-icon class="eye-icon">👁</el-icon>
                    <router-link to="/report_view" class="menu-link">报告查看</router-link>
                  </el-menu-item>
                </div>
              </el-sub-menu>

              <el-sub-menu index="2" class="menu-group">
                <template #title>
                  <div class="menu-title">
                    <el-icon class="menu-icon">
                      <Location />
                    </el-icon>
                    <span>翻译智能体</span>
                  </div>
                </template>
                <div class="submenu-group">
                  <div class="group-label">大模型翻译</div>
                  <el-menu-item index="/textTranslation" class="menu-item">
                    <el-icon>
                      <Document />
                    </el-icon>
                    <router-link to="/wbfy" class="menu-link">文本翻译</router-link>
                  </el-menu-item>
                  <el-menu-item index="/documentTranslation" class="menu-item">
                    <el-icon>
                      <Notebook />
                    </el-icon>
                    <router-link to="/wdfy" class="menu-link">文档翻译</router-link>
                  </el-menu-item>

                  <el-menu-item index="/ckgl" class="menu-item">
                    <el-icon>
                      <ChatDotSquare />
                    </el-icon>
                    <router-link to="/ckgl" class="menu-link">词库管理</router-link>
                  </el-menu-item>

                </div>
              </el-sub-menu>


              <el-sub-menu index="5" class="menu-group">
                <template #title>
                  <div class="menu-title">
                    <el-icon>
                      <MessageBox />
                    </el-icon>
                    <span>知识库</span>
                  </div>
                </template>
                <div class="submenu-group">
                  <el-menu-item index="/public_db" class="menu-item">
                    <el-icon>
                      <Collection />
                    </el-icon>
                    <router-link to="/public_db" class="menu-link">公共知识库</router-link>
                  </el-menu-item>
                  <el-menu-item index="/zskck" class="menu-item">
                    <el-icon>
                      <Message />
                    </el-icon>
                    <router-link to="/zskck" class="menu-link">个人知识库</router-link>
                  </el-menu-item>
                </div>
              </el-sub-menu>

            </el-menu>
          </div>
        </el-aside>

        <!-- 主内容区域 -->
        <el-main class="main-content">
          <div class="content-wrapper">
            <router-view></router-view>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>

  <!-- 个人设置弹窗 -->
  <el-dialog v-model="showAccountSettingModal" title="个人设置" width="500px" append-to-body destroy-on-close
    class="square-dialog">
    <count-setting />
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="showAccountSettingModal = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 关于系统弹窗 -->
  <el-dialog v-model="showAboutModal" title="关于系统" width="600px" append-to-body destroy-on-close class="square-dialog">
    <about-system />
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="showAboutModal = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { getUserIdFromCookie, logoutUser, getUserNameFromCookie, getExpireTimeFromCookie } from '@/utils/authUtils'
import {
  Document,
  Location,
  Collection,
  Connection,
  MessageBox,
  Message,
  ChatDotSquare,
  EditPen,
  Edit,
  SwitchButton,
  InfoFilled,
  Expand,
  Fold
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import CountSetting from '@/components/zhanghu/count_setting.vue'
import AboutSystem from '@/components/zhanghu/about_system.vue'

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前cookie中的用户ID
const currentUserId = ref<string | null>(null)
const currentUserName = ref<string | null>(null)
const showAccountSettingModal = ref(false)
const showAboutModal = ref(false)
const router = useRouter()

// 存储真实的登录状态，使得Vue能响应其变化
const isLoggedInStatus = ref(getUserIdFromCookie() !== null);

// 计算属性：判断用户是否已登录，兼容模板
const isLoggedIn = computed(() => {
  return isLoggedInStatus.value;
})

// 计算属性：获取用户名的首字母作为头像
const userInitial = computed(() => {
  if (!currentUserName.value || currentUserName.value === '未登录') return '?';
  return currentUserName.value.charAt(0).toUpperCase();
})

let cookieCheckInterval: any = null;

// 组件挂载时获取当前用户ID
onMounted(() => {
  const userName = getUserNameFromCookie();
  currentUserName.value = userName !== null ? userName : '未登录';

  // 轮询检查cookie是否到期
  cookieCheckInterval = setInterval(() => {
    const hasUserId = getUserIdFromCookie() !== null;

    // 获取单独的截止日期字段
    const expireTime = getExpireTimeFromCookie();
    const isExpired = expireTime ? new Date().getTime() > expireTime : false;

    // 只有既有用户ID，且截止日期没有过期，才认为有效
    const valid = hasUserId && !isExpired;

    if (isLoggedInStatus.value !== valid) {
      isLoggedInStatus.value = valid;
    }
    // 如果检查到cookie失效（未登录或时间已到），且当前路由不是登录页，强制跳转登出
    if (!valid && router.currentRoute.value.path !== '/login') {
      logoutUser(); // 清除可能残留的无效cookie
      router.push('/login');
    }
  }, 1000);
})

// 组件销毁时清除定时器
onUnmounted(() => {
  if (cookieCheckInterval) {
    clearInterval(cookieCheckInterval);
  }
})

// 处理注销功能
const handleLogout = () => {
  try {
    // 调用注销函数，清除cookie中的user_id
    logoutUser();
    // 显示注销成功提示
    ElMessage.success('注销成功');
    // 刷新页面，跳转到登录页
    window.location.reload();
  } catch (error) {
    console.error('注销失败:', error);
    ElMessage.error('注销失败，请重试');
  }
}

const handleOpen = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}

const handleClose = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
</script>

<style scoped>
/* 登录容器样式，让登录页面占满整个屏幕 */
.login-container {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  background: #f0f2f5;
}

.research-layout {
  height: 100vh;
  width: 100vw;
  background: #eef0f3;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
}

.main-container {
  height: 100%;
  box-shadow: none;
  border-radius: 0;
  margin: 0;
  overflow: hidden;
  background: #f4f6f8;
}

/* 顶部导航栏样式 — 深海军蓝，科研机构风格 */
.header {
  background: #1a2b4a;
  color: white;
  padding: 0 28px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
  height: 56px !important;
  border-bottom: 2px solid #0f5ea8;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #e8edf5;
  transition: color 0.3s;
}

.collapse-btn:hover {
  color: #3b82f6;
}

.system-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #e8edf5;
  letter-spacing: 0.5px;
}

.title-icon {
  font-size: 20px;
  color: #5ba4e0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 当前用户ID显示样式 */
.id-value {
  font-weight: 500;
  color: #a8c4e0;
  margin-right: 4px;
  font-size: 13px;
}

.user-avatar-circle {
  width: 32px;
  height: 32px;
  background-color: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  user-select: none;
  flex-shrink: 0;
}

.user-avatar-circle.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.user-avatar-circle.clickable:hover {
  transform: scale(1.05);
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.5);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

/* 主体容器样式 */
.body-container {
  height: calc(100% - 56px);
}

/* 侧边栏样式 — 白底、左蓝边框点缀 */
.sidebar {
  width: 180px !important;
  background: #ffffff;
  border-right: 1px solid #d6dce6;
  overflow-y: auto;
  transition: width 0.3s;
}

.sidebar.is-collapsed {
  width: 64px !important;
}

.sidebar-content {
  padding: 16px 0;
  /* 折叠收缩时去掉左右边距以保证对齐 */
}

.sidebar-menu {
  border: none;
  background: transparent;
}

.menu-group {
  margin-bottom: 4px;
}

.menu-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #1a2b4a;
  font-size: 13px;
}

.menu-icon {
  font-size: 16px;
  color: #2664a8;
}

.submenu-group {
  padding-left: 8px;
  margin-top: 4px;
}

.group-label {
  font-size: 11px;
  color: #8a9ab5;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 4px;
  padding-left: 12px;
  margin-top: 8px;
  font-weight: 600;
}

.menu-item {
  margin: 2px 0;
  border-radius: 3px;
  transition: background 0.15s ease;
}

.menu-item:hover {
  background-color: #eaf1fb;
  transform: none;
}

.menu-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  width: 100%;
}

.eye-icon {
  font-size: 15px;
}

/* 主内容区域样式 */
.main-content {
  width: 100%;
  height: 100%;
  background: #f4f6f8;
  padding: 0px;
}

.content-wrapper {
  width: 100%;
  height: 100%;
  background: #f4f6f8;
  border-radius: 0;
  box-shadow: none;
  padding: 0px;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu--collapse .el-sub-menu__title span),
:deep(.el-menu--collapse .submenu-group) {
  display: none;
}

:deep(.el-sub-menu__title) {
  height: 44px;
  line-height: 44px;
  padding-left: 12px !important;
  border-radius: 3px;
  margin: 2px 0;
  transition: background 0.15s ease;
  color: #1a2b4a;
  font-size: 13px;
}

:deep(.el-sub-menu__title:hover) {
  background-color: #eaf1fb;
}

:deep(.el-menu-item) {
  height: 38px;
  line-height: 38px;
  padding-left: 28px !important;
  border-radius: 3px;
  margin: 1px 0;
  font-size: 13px;
  color: #3a4a62;
}

:deep(.el-menu-item.is-active) {
  background-color: #ddeeff;
  color: #1a5caa;
  font-weight: 600;
  border-left: 3px solid #1a5caa;
}

:deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 15px;
  color: #2664a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .research-layout {
    margin: 0;
  }

  .main-container {
    margin: 0;
    border-radius: 0;
  }

  .sidebar {
    width: 180px !important;
  }

  .system-title {
    font-size: 16px;
  }
}
</style>