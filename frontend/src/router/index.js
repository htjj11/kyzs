import { createRouter, createWebHistory } from 'vue-router'
import { getUserIdFromCookie } from '@/utils/authUtils'

// 导入登录组件
import login from "@/login.vue"

// 检查用户是否已登录的函数
const isUserLoggedIn = () => {
  // 使用统一的authUtils中的函数进行检查
  return getUserIdFromCookie() !== null;
};

// 这里是路由和组件的绑定关系
// 为了提高性能，所有页面组件均使用路由懒加载（动态导入）
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: login,
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      redirect: '/literatureSearch'
    },

    // ----------------- 报告智能体 -----------------
    {
      // 文献检索
      path: '/literatureSearch',
      name: 'literatureSearch',
      component: () => import("@/components/报告智能体/文献检索.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 专利检索
      path: '/patentSearch',
      name: 'patentSearch',
      component: () => import("@/components/报告智能体/专利检索.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 网络信息检索
      path: '/webinfoSearch',
      name: 'webinfoSearch',
      component: () => import("@/components/报告智能体/网络信息检索.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 个人知识库上传
      path: '/fileUpload',
      name: 'fileUpload',
      component: () => import("@/components/报告智能体/个人知识库上传.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 个人知识库
      path: '/zskck',
      name: 'zskck',
      component: () => import("@/components/报告智能体/个人知识库.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 报告管理
      path: '/report_view',
      name: 'report_view',
      component: () => import("@/components/报告智能体/报告管理.vue"),
      meta: { requiresAuth: true }
    },
    {
      // new_editor
      path: '/new_editor',
      name: 'new_editor',
      component: () => import("@/components/报告智能体/报告管理/报告编辑器.vue"),
      meta: { requiresAuth: true }
    },

    // ----------------- 翻译智能体 -----------------
    {
      // 文本翻译
      path: '/wbfy',
      name: 'wbfy',
      component: () => import("@/components/翻译智能体/文本翻译.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 文档翻译
      path: '/wdfy',
      name: 'wdfy',
      component: () => import("@/components/翻译智能体/文档翻译.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 词库管理
      path: '/ckgl',
      name: 'ckgl',
      component: () => import("@/components/翻译智能体/词库管理.vue"),
      meta: { requiresAuth: true }
    },

    // ----------------- 公共知识库 -----------------
    {
      // 公共知识库主页
      path: '/public_db',
      name: 'public_db',
      component: () => import("@/components/公共知识库/公共知识库主页.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 公共知识库上传
      path: '/public_db_upload',
      name: 'public_db_upload',
      component: () => import("@/components/公共知识库/公共知识库上传.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 公共知识库对话
      path: '/public_db_chat',
      name: 'public_db_chat',
      component: () => import("@/components/公共知识库/公共知识库对话.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 公共知识库查看
      path: '/public_db_view',
      name: 'public_db_view',
      component: () => import("@/components/公共知识库/公共知识库查看.vue"),
      meta: { requiresAuth: true }
    },

    // ----------------- 系统 -----------------
    {
      // 关于系统
      path: '/system_about',
      name: 'system_about',
      component: () => import("@/components/系统/关于系统.vue"),
      meta: { requiresAuth: true }
    },
    {
      // 账户设置
      path: '/account_settings',
      name: 'account_settings',
      component: () => import("@/components/系统/账户设置.vue"),
      meta: { requiresAuth: true }
    },

    // 捕获所有未匹配的路由，重定向到登录页面
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  const requiresAuth = to.meta.requiresAuth !== false; // 默认需要认证
  const isLoggedIn = isUserLoggedIn();

  // 特殊处理：如果用户已登录且尝试访问登录页面，则重定向到首页
  if (isLoggedIn && to.path === '/login') {
    next('/'); // 重定向到首页或其他合适的页面
  }
  // 普通情况：需要认证但未登录，重定向到登录页面
  else if (requiresAuth && !isLoggedIn) {
    next('/login');
  }
  // 其他情况：允许访问
  else {
    next();
  }
});

export default router