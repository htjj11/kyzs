// 服务的统一 API URL 配置
// 提示：该变量现由 vite.config.js 从 C:\.env.vuehost 动态注入
const api_url = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export default api_url;