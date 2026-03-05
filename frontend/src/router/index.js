import {createRouter, createWebHashHistory, createWebHistory} from 'vue-router'
import { getUserIdFromCookie } from '@/utils/authUtils'

// 导入登录组件
import login from "@/login.vue"

// 若 "@/components/wxjs.vue" 解析失败，尝试使用相对路径导入
// 假设该文件相对于当前文件的路径是 "../components/wxjs.vue"，请根据实际目录结构调整
import wxjs from "@/components/baogao/1wxjs.vue";
import wxjsjh from "@/components/baogao/1.2article_juhe.vue";
import wxjsWanfang from "@/components/baogao/1.3article_wanfang.vue";
import zljs from "@/components/baogao/2zljs.vue";
import zljs_wanfang from "@/components/baogao/2.1zljs_wanfnag.vue";
import wlxxjs from "@/components/baogao/3wlxxjs.vue";
import zlsc from "@/components/baogao/4zlsc.vue";
import zskck from "@/components/baogao/5zskck.vue";
import zsck from "@/components/baogao/zsck.vue";
import zsck2 from "@/components/baogao/zsck2.vue";
import new_editor from "@/components/baogao/new_editor.vue";


import qtsz from "@/components/qtsz.vue";

import wbfy from "@/components/fanyi/wbfy.vue";
import wdfy from "@/components/fanyi/wdfy.vue";
import ckgl from "@/components/fanyi/ckgl.vue";



import wenda from "@/components/wenda/wenda.vue";
import db_manage from "@/components/wenda/db_manage.vue";
import all_db from "@/components/wenda/all_db.vue";

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
      redirect: '/wxjs' // 默认重定向到文献检索页面
    },
    {      
      path: '/wxjsjh',
      name: 'wxjsjh',
      component: wxjsjh,
      meta: { requiresAuth: true }
    },
    {
      path: '/wxjs_wanfang',
      name: 'wxjs_wanfang',
      component: wxjsWanfang,
      meta: { requiresAuth: true }
    },

    {
      path: '/wxjs',
      name: 'wxjs',
      component: wxjs,
      meta: { requiresAuth: true }
    },
    {
      path: '/zljs',
      name: 'zljs',
      component: zljs,
      meta: { requiresAuth: true }
    },
    {
      path: '/zljs_wanfang',
      name: 'zljs_wanfang',
      component: zljs_wanfang,
      meta: { requiresAuth: true }
    },
    {
      path: '/zsck',
      name: 'zsck',
      component: zsck,
      meta: { requiresAuth: true }
    },
    {
      path: '/zsck2',
      name: 'zsck2',
      component: zsck2,
      meta: { requiresAuth: true }
    },
    {
      path: '/zskck',
      name: 'zskck',
      component: zskck,
      meta: { requiresAuth: true }
    },
    
    {
      path: '/zlsc',
      name: 'zlsc',
      component: zlsc,
      meta: { requiresAuth: true }
    },
    {
      path: '/qtsz',
      name: 'qtsz',
      component: qtsz,
      meta: { requiresAuth: true }
    },
    {
      path: '/wlxxjs',
      name: 'wlxxjs',
      component: wlxxjs,
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
      path: '/wenda',
      name: 'wenda',
      component: wenda,
      meta: { requiresAuth: true }
    },
    {
      path: '/db_manage',
      name: 'db_manage',
      component: db_manage,
      meta: { requiresAuth: true }
    },
    {
      path: '/all_db',
      name: 'all_db',
      component: all_db,
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