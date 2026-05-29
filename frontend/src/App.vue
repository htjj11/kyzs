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
        <el-button
          v-if="isSuperAdmin"
          type="danger"
          plain
          @click="showSuperAdminModal = true"
        >
          超级管理员
        </el-button>
        <el-button @click="showAboutModal = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- 超级管理员弹窗（仅 admin:admin 权限可见入口） -->
  <el-dialog
    v-model="showSuperAdminModal"
    title="超级管理员"
    width="720px"
    append-to-body
    destroy-on-close
    class="square-dialog"
  >
    <super-admin-permission />
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="showSuperAdminModal = false">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import {
  getUserIdFromCookie,
  logoutUser,
  getUserNameFromCookie,
  getExpireTimeFromCookie,
  hasSuperAdminPermission
} from '@/utils/authUtils'
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
import CountSetting from '@/components/系统/账户设置.vue'
import AboutSystem from '@/components/系统/关于系统.vue'
import SuperAdminPermission from '@/components/系统/超级管理员权限.vue'

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前cookie中的用户ID
const currentUserId = ref<string | null>(null)
const currentUserName = ref<string | null>(null)
const showAccountSettingModal = ref(false)
const showAboutModal = ref(false)
const showSuperAdminModal = ref(false)
const router = useRouter()

const isSuperAdmin = computed(() => hasSuperAdminPermission())

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

    // 同步更新用户名（修复 SSO 首次登录显示“未登录”的问题）
    const userName = getUserNameFromCookie();
    currentUserName.value = userName !== null ? userName : (valid ? currentUserName.value : '未登录');

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
/* 登录容器样式匹配 */
.login-container {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0;
  background: #0b0f19;
  /* 与登录页面的底层夜色匹配，防止闪屏 */
}

/* 整个应用底层背景：高级液态光效 (Light mode glass) */
.research-layout {
  height: 100vh;
  width: 100vw;
  background-color: #f2f5f9;
  background-image:
    radial-gradient(circle at 10% 20%, rgba(0, 195, 255, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 90% 80%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(147, 51, 234, 0.06) 0%, transparent 60%);
  font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
}

.main-container {
  height: 100%;
  box-shadow: none;
  border-radius: 0;
  margin: 0;
  overflow: hidden;
  background: transparent;
}

/* 顶部导航栏：悬浮玻璃 */
.header {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(48px) saturate(180%);
  -webkit-backdrop-filter: blur(48px) saturate(180%);
  color: #1a2b4a;
  padding: 0 20px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
  height: 52px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.6);
  z-index: 10;
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
  font-size: 18px;
  cursor: pointer;
  color: #4a5568;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.collapse-btn:hover {
  color: #007aff;
  transform: scale(1.05);
}

.system-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: #1a2b4a;
  letter-spacing: 0.5px;
}

.title-icon {
  font-size: 18px;
  color: #007aff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 当前用户ID显示样式 */
.id-value {
  font-weight: 600;
  color: #64748b;
  margin-right: 4px;
  font-size: 13px;
}

.user-avatar-circle {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #007aff 0%, #00d4ff 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.5);
  user-select: none;
  flex-shrink: 0;
}

.user-avatar-circle.clickable {
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.user-avatar-circle.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 122, 255, 0.4);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}

/* 主体容器样式 */
.body-container {
  height: calc(100% - 52px);
}

/* 侧边栏：液态毛玻璃 */
.sidebar {
  width: 200px !important;
  background: rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border-right: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 2px 0 24px rgba(0, 0, 0, 0.02);
  overflow-y: auto;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 5;
}

.sidebar.is-collapsed {
  width: 64px !important;
}

.sidebar-content {
  padding: 8px 0;
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
  gap: 8px;
  font-weight: 700;
  color: #1a2b4a;
  font-size: 13px;
}

.submenu-group {
  padding-left: 8px;
  margin-top: 2px;
  margin-bottom: 4px;
}

.group-label {
  font-size: 11px;
  color: #8a9ab5;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
  padding-left: 12px;
  margin-top: 6px;
  font-weight: 700;
}

.menu-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  width: 100%;
  height: 100%;
}

.eye-icon {
  font-size: 14px;
}

/* 主内容区域：稍微透明给内部卡片留出空间，去除外部滚动条 */
.main-content {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  background: transparent;
  padding: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-wrapper {
  flex: 1;
  width: 100%;
  min-height: 0;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Element Plus 玻璃拟物化菜单样式覆盖 */
:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu--collapse .el-sub-menu__title span),
:deep(.el-menu--collapse .submenu-group) {
  display: none;
}

:deep(.el-sub-menu__title) {
  height: 38px;
  line-height: 38px;
  padding-left: 14px !important;
  border-radius: 8px;
  margin: 2px 8px;
  transition: all 0.3s ease;
  color: #1a2b4a;
  font-size: 13px;
}

:deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.6);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

:deep(.el-menu-item) {
  height: 34px;
  line-height: 34px;
  padding-left: 30px !important;
  border-radius: 8px;
  margin: 2px 8px;
  font-size: 13px;
  font-weight: 500;
  color: #4a5568;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.8);
  transform: translateX(3px);
}

:deep(.el-menu-item.is-active) {
  background-color: rgba(0, 122, 255, 0.08);
  color: #007aff;
  font-weight: 700;
  box-shadow: inset 0 0 0 1px rgba(0, 122, 255, 0.15);
  border-left: none;
  /* 移除旧的粗左边框设计 */
}

:deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 15px;
  color: #64748b;
  transition: all 0.3s ease;
}

:deep(.el-menu-item.is-active .el-icon) {
  color: #007aff;
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
    width: 200px !important;
  }

  .system-title {
    font-size: 18px;
  }

  .main-content {
    padding: 10px;
  }

  .content-wrapper {
    border-radius: 20px;
  }
}
</style>