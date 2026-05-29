/**
 * crypto.randomUUID() polyfill
 * TinyMCE 8 内部依赖此 API，旧版浏览器不支持，需手动补丁
 */
if (typeof window.crypto === 'undefined') {
  window.crypto = {};
}
if (!window.crypto.randomUUID) {
  window.crypto.randomUUID = function () {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
      const r = (Math.random() * 16) | 0;
      const v = c === 'x' ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  };
}

import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'; // 引入中文语言包
import router from './router'
import axios from "./api/request.js"; //引入request.js


const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.use(ElementPlus, { locale: zhCn }).use(router).mount('#app')

app.config.globalProperties.$axios = axios; //配置axios的全局引用