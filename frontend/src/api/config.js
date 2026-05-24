// 服务的统一 API URL 配置
// 提示：以下变量可由 vite.config.js 从 C:\.env.vuehost 动态注入
export const api_url =  'https://10.68.202.238:8443';

// RAGFlow 服务主机（.env.vuehost 中 RAGFLOW_API_IP = http://192.168.137.130）
export const ragflow_api_ip =  'http://192.168.137.130';

// RAGFlow 对话页完整地址（未配置完整 URL 时，默认基于 ragflow_api_ip 拼接）
const defaultRagflowShareUrl =
  `${ragflow_api_ip.replace(/\/$/, '')}/next-search/share?shared_id=6786357235bf11f1aeed9bfd9c11ebc2&from=search&auth=QKiedFFs9sfN33vrtBWgDLUleec5WxVg&tenantId=2b72a9ca212a11f18ea4fbdc65029751`;

export const ragflow_url =
  import.meta.env.VITE_RAGFLOW_API_BASE_URL ||
  import.meta.env.RAGFLOW_API_BASE_URL ||
  defaultRagflowShareUrl;

