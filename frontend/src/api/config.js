// 服务的统一 API URL 配置
// 提示：该变量现由 vite.config.js 从 C:\.env.vuehost 动态注入
const api_url = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// 增加 RAGFlow 的服务配置字符串 
// 兼容 VITE_RAGFLOW_API_BASE_URL (规范写法) 或者普通的 RAGFLOW_API_BASE_URL
export const ragflow_url = import.meta.env.VITE_RAGFLOW_API_BASE_URL || import.meta.env.RAGFLOW_API_BASE_URL || 'http://192.168.137.130/next-search/share?shared_id=6786357235bf11f1aeed9bfd9c11ebc2&from=search&auth=QKiedFFs9sfN33vrtBWgDLUleec5WxVg&tenantId=2b72a9ca212a11f18ea4fbdc65029751';

export default api_url;