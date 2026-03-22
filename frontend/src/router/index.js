import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router'
import { getUserIdFromCookie } from '@/utils/authUtils'

// 导入登录组件
import login from "@/login.vue"

// 若 "@/components/wxjs.vue" 解析失败，尝试使用相对路径导入
// 假设该文件相对于当前文件的路径是 "../components/wxjs.vue"，请根据实际目录结构调整
import literatureSearch from "@/components/baogao/literature_search.vue";
import patentSearch from "@/components/baogao/patent_search.vue";
import webinfoSearch from "@/components/baogao/webinfo_search.vue";
import fileUpload from "@/components/baogao/file_upload.vue";
import zskck from "@/components/baogao/5zskck.vue";
import report_view from "@/components/baogao/report_view.vue";
import new_editor from "@/components/baogao/new_editor.vue";

import wbfy from "@/components/fanyi/wbfy.vue";
import wdfy from "@/components/fanyi/wdfy.vue";
import ckgl from "@/components/fanyi/ckgl.vue";
import public_db from "@/components/public_db/public_db.vue";



// 检查用户是否已登录的函数
const isUserLoggedIn = () => {
  // 使用统一的authUtils中的函数进行检查
  return getUserIdFromCookie() !== null;
};

//这里是路由和组件的绑定关系
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
    {
      //文献搜索
      path: '/literatureSearch',
      name: 'literatureSearch',
      component: literatureSearch,
      meta: { requiresAuth: true }
    },
    {
      //专利检索
      path: '/patentSearch',
      name: 'patentSearch',
      component: patentSearch,
      meta: { requiresAuth: true }
    },
    {
      //资料上传
      path: '/fileUpload',
      name: 'fileUpload',
      component: fileUpload,
      meta: { requiresAuth: true }
    },
    {
      path: '/report_view',
      name: 'report_view',
      component: report_view,
      meta: { requiresAuth: true }
    },
    {
      path: '/zskck',
      name: 'zskck',
      component: zskck,
      meta: { requiresAuth: true }
    },
    {
      path: '/webinfoSearch',
      name: 'webinfoSearch',
      component: webinfoSearch,
      meta: { requiresAuth: true }
    },
    {
      path: '/wbfy',
      name: 'wbfy',
      component: wbfy,
      meta: { requiresAuth: true }
    },
    {
      path: '/wdfy',
      name: 'wdfy',
      component: wdfy,
      meta: { requiresAuth: true }
    },
    {
      path: '/ckgl',
      name: 'ckgl',
      component: ckgl,
      meta: { requiresAuth: true }
    },
    {
      path: '/public_db',
      name: 'public_db',
      component: public_db,
      meta: { requiresAuth: true }
    },

    // 捕获所有未匹配的路由，重定向到登录页面
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    },
    {
      path: '/new_editor',
      name: 'new_editor',
      component: new_editor,
      meta: { requiresAuth: true }
    },
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