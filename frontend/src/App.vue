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
          <h1 class="system-title">
            <el-icon class="title-icon">
              <Document />
            </el-icon>
            科研情报系统
          </h1>
          <div class="header-actions">
            <span class="id-value">{{ currentUserName }}</span>
            <el-button type="warning" size="small" @click="handleLogout">
              注销
            </el-button>
            <el-button type="primary" size="small" circle>
              <el-icon>
                <Setting />
              </el-icon>
            </el-button>
          </div>
        </div>
      </el-header>

      <el-container class="body-container">
        <!-- 侧边栏 -->
        <el-aside class="sidebar">
          <div class="sidebar-content">
            <el-menu default-active="1" class="sidebar-menu" @open="handleOpen" @close="handleClose"
              background-color="transparent" text-color="#4a5568" active-text-color="#3b82f6">
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
                  <el-menu-item index="/fileUpload" class="menu-item">
                    <el-icon>
                      <Upload />
                    </el-icon>
                    <router-link to="/fileUpload" class="menu-link">个人资料上传</router-link>
                  </el-menu-item>

                </div>

                <div class="submenu-group">
                  <div class="group-label">报告管理</div>
                  <el-menu-item index="3" class="menu-item">
                    <el-icon class="eye-icon">👁‍🗨</el-icon>
                    <router-link to="/zsck" class="menu-link">报告</router-link>
                  </el-menu-item>
                  <el-menu-item index="4" class="menu-item">
                    <el-icon class="eye-icon">👁‍🗨</el-icon>
                    <router-link to="/zsck2" class="menu-link">报告(新版编辑器)</router-link>
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

              <el-sub-menu index="3" class="menu-group">
                <template #title>
                  <div class="menu-title">
                    <el-icon>
                      <ChatDotSquare />
                    </el-icon>
                    <span>大模型知识库问答</span>
                  </div>
                </template>
                <el-menu-item index="/webTranslation" class="menu-item">
                  <el-icon>
                    <EditPen />
                  </el-icon>
                  <router-link to="/wenda" class="menu-link">问答对话</router-link>
                </el-menu-item>


              </el-sub-menu>

              <el-sub-menu index="5" class="menu-group">
                <template #title>
                  <div class="menu-title">
                    <el-icon>
                      <MessageBox />
                    </el-icon>
                    <span>知识库管理</span>
                  </div>
                </template>
                <div class="submenu-group">
                  <el-menu-item index="/all_db" class="menu-item">
                    <el-icon>
                      <MessageBox />
                    </el-icon>
                    <router-link to="/all_db" class="menu-link">公共知识库查看</router-link>
                  </el-menu-item>
                  <el-menu-item index="/db_manage" class="menu-item">
                    <el-icon>
                      <MessageBox />
                    </el-icon>
                    <router-link to="/db_manage" class="menu-link">公共知识库管理</router-link>
                  </el-menu-item>
                  <el-menu-item index="/zskck" class="menu-item">
                    <el-icon>
                      <Message />
                    </el-icon>
                    <router-link to="/zskck" class="menu-link">个人知识库管理</router-link>
                  </el-menu-item>
                </div>
              </el-sub-menu>
              <el-menu-item index="4" class="menu-item">
                <router-link to="/qtsz" class="menu-link">其他设置</router-link>
              </el-menu-item>
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
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getUserIdFromCookie, logoutUser } from '@/utils/authUtils'
import {
  Document,
  Location,
  Setting,
  Collection,
  Connection,
  Upload,
  MessageBox,
  Message,
  ChatDotSquare,
  EditPen
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getUserNameFromCookie } from '@/utils/authUtils'

// 当前cookie中的用户ID
const currentUserId = ref<string | null>(null)
const currentUserName = ref<string | null>(null)
const router = useRouter()

// 计算属性：判断用户是否已登录
const isLoggedIn = computed(() => {
  const userId = getUserIdFromCookie();
  // 只要userId存在且不为null，则认为已登录
  return userId !== null;
})

// 组件挂载时获取当前用户ID
onMounted(() => {
  const userName = getUserNameFromCookie();
  currentUserName.value = userName !== null ? userName : '未登录';
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
  margin-left: 4px;
  font-size: 13px;
}

/* 主体容器样式 */
.body-container {
  height: calc(100% - 56px);
}

/* 侧边栏样式 — 白底、左蓝边框点缀 */
.sidebar {
  width: 260px !important;
  background: #ffffff;
  border-right: 1px solid #d6dce6;
  overflow-y: auto;
}

.sidebar-content {
  padding: 16px 12px;
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
    width: 220px !important;
  }

  .system-title {
    font-size: 16px;
  }
}
</style>