<template>
  <div class="chat-container">
    <!-- HTTPS 页面无法 iframe 嵌入 HTTP 资源（浏览器安全策略），改用新标签页打开 -->
    <div class="chat-placeholder">
      <el-icon :size="48" color="#909399"><Monitor /></el-icon>
      <p class="placeholder-text">RAGFlow 知识库对话服务需在新窗口中打开</p>
      <el-button type="primary" size="large" @click="openRagflow">
        <el-icon style="margin-right: 6px"><Right /></el-icon>打开知识库对话
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ragflow_url } from '@/api/config.js'
import { Monitor, Right } from '@element-plus/icons-vue'

const openRagflow = () => {
  window.open(ragflow_url, '_blank')
}
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  min-height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 60px 40px;
}

.placeholder-text {
  font-size: 16px;
  color: #606266;
  margin: 0;
}
</style>
