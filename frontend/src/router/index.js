import { createRouter, createWebHistory } from 'vue-router'
import { getUserIdFromCookie, setUserIdCookie, setUserNameCookie, setExpireTimeCookie, setPermissionCookie, setRagflowIdCookie } from '@/utils/authUtils'
import { api_url } from '@/api/config'

// 导入登录组件
import login from "@/login.vue"

// 检查用户是否已登录的函数
const isUserLoggedIn = () => {
  return getUserIdFromCookie() !== null;
};

// SSO 登录：调用后端接口校验 tk，成功后写 cookie
async function doSsoLogin(tk) {
  try {
    const res = await fetch(`${api_url}/system/sso_login?tk=${encodeURIComponent(tk)}`);
    const json = await res.json();
    if (json.code === 200 && json.data) {
      const { user_id, user_name, permission, ragflow_id } = json.data;
      const minutes = 480; // 8小时有效期
      setUserIdCookie(user_id, minutes);
      setUserNameCookie(user_name, minutes);
      setExpireTimeCookie(Date.now() + minutes * 60 * 1000, minutes);
      setPermissionCookie(permission, minutes);
      setRagflowIdCookie(ragflow_id, minutes);
      return true;
    }
    console.error('SSO 校验失败：', json.msg);
    return false;
  } catch (e) {
    console.error('SSO 请求异常：', e);
    return false;
  }
}

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
      // 个人知识库 RAG 检索
      path: '/personal_kb_search',
      name: 'personal_kb_search',
      component: () => import("@/components/报告智能体/个人知识库检索.vue"),
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
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.meta.requiresAuth !== false;
  const tk = to.query.tk; // 获取 URL 中的 SSO token
  console.log('tk:', tk);
  // 如果 URL 携带 tk 参数，尝试 SSO 登录
  if (tk) {
    const ok = await doSsoLogin(tk);
    if (ok) {
      // SSO 成功，去掉 tk 参数后跳转，防止 tk 残留在地址栏
      const query = { ...to.query };
      delete query.tk;
      return next({ path: to.path, query, replace: true });
    } else {
      // SSO 失败，跳转到登录页并提示
      alert('您没有登录权限。');
      return next('/login');
    }
  }

  const isLoggedIn = isUserLoggedIn();

  // 已登录且访问登录页，跳到首页
  if (isLoggedIn && to.path === '/login') {
    return next('/');
  }
  // 需要认证但未登录，跳转到外部统一登录入口
  else if (requiresAuth && !isLoggedIn) {
    window.location.href = 'https://10.68.16.92/';
    return;
  }
  // 其他情况放行
  else {
    return next();
  }
});

export default router