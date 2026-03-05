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
            <el-icon class="title-icon"><Document /></el-icon>
            科研情报系统
          </h1>
          <div class="header-actions">
             <span class="id-value">{{ currentUserName }}</span>
            <el-button type="warning" size="small" @click="handleLogout">
              注销
            </el-button>
            <el-button type="primary" size="small" circle>
              <el-icon><Setting /></el-icon>
            </el-button>
          </div>
        </div>
      </el-header>
      
      <el-container class="body-container">
        <!-- 侧边栏 -->
        <el-aside class="sidebar">
          <div class="sidebar-content">
            <el-menu
              default-active="1"
              class="sidebar-menu"
              @open="handleOpen"
              @close="handleClose"
              background-color="transparent"
              text-color="#4a5568"
              active-text-color="#3b82f6"
            >
              <el-sub-menu index="1" class="menu-group">
                <template #title>
                  <div class="menu-title">
                    <el-icon class="menu-icon"><Location /></el-icon>
                    <span>报告智能体</span>
                  </div>
                </template>
                <div class="submenu-group">
                  <div class="group-label">知识信息检索</div>
                  <el-sub-menu index="/wxjs" class="menu-sub">
                    <template #title>
                      
                      <span style="margin-left: 17px;">
                        <el-icon class="submenu-icon"><Document /></el-icon>
                        文献检索
                      </span>
                    </template>
                    <el-menu-item index="/wxjs" class="menu-item">
                      <span style="margin-left: 17px;">
                        <router-link to="/wxjs" class="menu-link">①文献检索（oilink资源）</router-link>
                      </span>
                    </el-menu-item>
                    <el-menu-item index="/wxjsjh" class="menu-item">
                      <span style="margin-left: 17px;">
                        <router-link to="/wxjsjh" class="menu-link">②文献检索（聚合）</router-link>
                      </span>
                    </el-menu-item>
                    <el-menu-item index="/wxjs_wanfang" class="menu-item">
                      <span style="margin-left: 17px;">
                        <router-link to="/wxjs_wanfang" class="menu-link">③万方文献检索</router-link>
                      </span>
                    </el-menu-item>
                  </el-sub-menu>
                  <el-sub-menu index="/zljs" class="menu-item">
                    <template #title>
                      <span style="margin-left: 17px;"><el-icon><Collection /></el-icon>专利检索</span>
                    </template>
                    <el-menu-item index="/zljs">
                       <span style="margin-left: 17px;">
                        <router-link to="/zljs" class="menu-link">Oilink专利检索</router-link>
                       </span>                      
                    </el-menu-item>
                    <el-menu-item index="/zljs_wanfang">
                      <span style="margin-left: 17px;">
                        <router-link to="/zljs_wanfang" class="menu-link">万方专利检索</router-link>
                      </span>                      
                    </el-menu-item>
                  </el-sub-menu>
                  <el-menu-item index="/wlxxjs" class="menu-item">
                    <el-icon><Connection /></el-icon>
                    <router-link to="/wlxxjs" class="menu-link">网络信息检索</router-link>
                  </el-menu-item>
                  <el-menu-item index="/zlsc" class="menu-item">
                    <el-icon><Upload /></el-icon>
                    <router-link to="/zlsc" class="menu-link">个人资料上传</router-link>
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
                    <el-icon class="menu-icon"><Location /></el-icon>
                    <span>翻译智能体</span>
                  </div>
                </template>
                <div class="submenu-group">
                  <div class="group-label">大模型翻译</div>
                  <el-menu-item index="/textTranslation" class="menu-item">
                    <el-icon><Document /></el-icon>
                    <router-link to="/wbfy" class="menu-link">文本翻译</router-link>
                  </el-menu-item>
                  <el-menu-item index="/documentTranslation" class="menu-item">
                    <el-icon><Notebook /></el-icon>
                    <router-link to="/wdfy" class="menu-link">文档翻译</router-link>
                  </el-menu-item>

                  <el-menu-item index="/ckgl" class="menu-item">
                    <el-icon><ChatDotSquare /></el-icon>
                    <router-link to="/ckgl" class="menu-link">词库管理</router-link>
                  </el-menu-item>

                </div>
              </el-sub-menu>

              <el-sub-menu index="3" class="menu-group">
                <template #title>
                  <div class="menu-title">
                    <el-icon><ChatDotSquare /></el-icon>
                    <span>大模型知识库问答</span>
                  </div>
                </template>
                <el-menu-item index="/webTranslation" class="menu-item">
                  <el-icon><EditPen /></el-icon>
                  <router-link to="/wenda" class="menu-link">问答对话</router-link>
                </el-menu-item>


              </el-sub-menu>
               
              <el-sub-menu index="5" class="menu-group">
                <template #title>
                  <div class="menu-title">
                    <el-icon><MessageBox /></el-icon>
                    <span>知识库管理</span>
                  </div>
                </template>
                <div class="submenu-group">
                  <el-menu-item index="/all_db" class="menu-item">
                    <el-icon><MessageBox /></el-icon>
                    <router-link to="/all_db" class="menu-link">公共知识库查看</router-link>
                  </el-menu-item>
                  <el-menu-item index="/db_manage" class="menu-item">
                    <el-icon><MessageBox /></el-icon>
                    <router-link to="/db_manage" class="menu-link">公共知识库管理</router-link>
                  </el-menu-item>
                  <el-menu-item index="/zskck" class="menu-item">
                    <el-icon><Message /></el-icon>
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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.research-layout {
  height: 96vh;
  width: 100vw;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.main-container {
  height: 100%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  margin: 16px;
  overflow: hidden;
  background: white;
}

/* 顶部导航栏样式 */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 64px !important;
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
  gap: 12px;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.title-icon {
  font-size: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 当前用户ID显示样式 */
.id-value {
  font-weight: 600;
  color: #fff;
  margin-left: 4px;
}

/* 主体容器样式 */
.body-container {
  height: calc(100% - 64px);
}

/* 侧边栏样式 */
.sidebar {
  width: 280px !important;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
}

.sidebar-content {
  padding: 24px 16px;
}

.sidebar-menu {
  border: none;
  background: transparent;
}

.menu-group {
  margin-bottom: 16px;
}

.menu-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: #2d3748;
}

.menu-icon {
  font-size: 18px;
  color: #4299e1;
}

.submenu-group {
  padding-left: 16px;
  margin-top: 8px;
}

.group-label {
  font-size: 12px;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
  padding-left: 16px;
}

.menu-item {
  margin: 4px 0;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background-color: #edf2f7;
  transform: translateX(4px);
}

.menu-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  width: 100%;
}

.eye-icon {
  font-size: 16px;
}

/* 主内容区域样式 */
.main-content {
  width: 100%;
  height: 100%;
  background: #ffffff;
  padding: 0px;
}

.content-wrapper {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 0px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 0px;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-sub-menu__title) {
  height: 48px;
  line-height: 48px;
  padding-left: 16px !important;
  border-radius: 8px;
  margin: 4px 0;
  transition: all 0.2s ease;
}

:deep(.el-sub-menu__title:hover) {
  background-color: #edf2f7;
}

:deep(.el-menu-item) {
  height: 40px;
  line-height: 40px;
  padding-left: 32px !important;
  border-radius: 6px;
  margin: 2px 0;
}

:deep(.el-menu-item.is-active) {
  background-color: #ebf8ff;
  color: #3182ce;
  font-weight: 500;
}

:deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 16px;
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
    width: 240px !important;
  }
  
  .system-title {
    font-size: 18px;
  }
}
</style>