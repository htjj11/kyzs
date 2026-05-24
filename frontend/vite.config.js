import { defineConfig } from 'vite';
import path from 'path';
import vue from '@vitejs/plugin-vue';
import fs from 'fs';

// 读取外部配置文件 C:\.env.vuehost（支持 KEY=value 或 KEY = value）
function getExternalEnvMap() {
  const envPath = 'C:/.env.vuehost';
  const map = {};
  if (!fs.existsSync(envPath)) return map;

  try {
    const content = fs.readFileSync(envPath, 'utf-8');
    for (const line of content.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const match = trimmed.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$/);
      if (match) map[match[1]] = match[2].trim();
    }
  } catch (e) {
    console.error('Failed to read C:\\.env.vuehost:', e);
  }
  return map;
}

const externalEnv = getExternalEnvMap();
const externalApiUrl = externalEnv.VITE_API_BASE_URL || null;
const externalRagflowApiIp =
  externalEnv.RAGFLOW_API_IP || externalEnv.VITE_RAGFLOW_API_IP || null;

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: path.resolve(__dirname, '../backend/frontend')
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  define: {
    'import.meta.env.VITE_API_BASE_URL': externalApiUrl
      ? JSON.stringify(externalApiUrl)
      : 'undefined',
    'import.meta.env.RAGFLOW_API_IP': externalRagflowApiIp
      ? JSON.stringify(externalRagflowApiIp)
      : 'undefined',
    'import.meta.env.VITE_RAGFLOW_API_IP': externalRagflowApiIp
      ? JSON.stringify(externalRagflowApiIp)
      : 'undefined'
  }
});
