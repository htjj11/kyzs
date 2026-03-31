import { defineConfig } from 'vite';
import path from 'path';
import vue from '@vitejs/plugin-vue';
import fs from 'fs';

// 读取外部配置文件 C:\.env.vuehost
function getExternalEnv() {
  const envPath = 'C:/.env.vuehost';
  if (fs.existsSync(envPath)) {
    try {
      const content = fs.readFileSync(envPath, 'utf-8');
      const match = content.match(/VITE_API_BASE_URL=(.+)/);
      if (match) return match[1].trim();
    } catch (e) {
      console.error('Failed to read C:\\.env.vuehost:', e);
    }
  }
  return null;
}

const externalApiUrl = getExternalEnv();

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  define: {
    // 注入外部定义的 API 地址，这会覆盖代码中的 import.meta.env.VITE_API_BASE_URL
    'import.meta.env.VITE_API_BASE_URL': externalApiUrl ? JSON.stringify(externalApiUrl) : 'undefined'
  }
})
