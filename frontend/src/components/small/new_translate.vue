<template>
  <div class="translate-upload-container">
    <div class="translate-upload-card">
      <div class="card-header">
        <h3 class="card-title">上传文档翻译</h3>
        <button @click="closeModal" class="close-button">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div class="card-body">
        <!-- PDF上传区域 -->
        <div class="upload-section">
          <label class="upload-label">选择PDF文件</label>
          <div 
            class="upload-area" 
            :class="{ 'has-file': selectedFile }"
            @click="triggerFileInput"
          >
            <input 
              ref="fileInput" 
              type="file" 
              accept=".pdf" 
              class="file-input" 
              @change="handleFileSelect"
            >
            
            <div v-if="!selectedFile" class="upload-placeholder">
              <svg class="upload-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <p class="upload-text">点击或拖拽文件到此处上传</p>
              <p class="upload-subtext">仅支持PDF格式，文件大小不超过20MB</p>
            </div>
            
            <div v-else class="file-info">
              <svg class="file-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="file-details">
                <p class="file-name">{{ selectedFile.name }}</p>
                <p class="file-size">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
              <button @click.stop="removeFile" class="remove-file-button">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 任务主题输入 -->
        <div class="topic-section">
          <label for="topic" class="topic-label">任务主题</label>
          <input 
            id="topic" 
            v-model="topic" 
            type="text" 
            class="topic-input" 
            placeholder="请输入翻译任务的主题描述"
            maxlength="100"
          >
          <p class="char-count">{{ topic.length }}/100</p>
        </div>
      </div>
      
      <div class="card-footer">
        <button 
          @click="closeModal" 
          class="cancel-button"
        >
          取消
        </button>
        <button 
          @click="uploadAndTranslate" 
          :disabled="!selectedFile || !topic.trim() || loading"
          class="translate-button"
        >
          <svg v-if="loading" class="animate-spin h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ loading ? '翻译中...' : '开始翻译' }}
        </button>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      <p class="error-text">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import request from '../../api/request';
import { getUserIdFromCookie } from '@/utils/authUtils';

// 响应式数据
const fileInput = ref(null)
const selectedFile = ref(null)
const topic = ref('')
const loading = ref(false)
const error = ref('')

// 触发文件选择
const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

// 处理文件选择
const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 检查文件类型
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      error.value = '请选择PDF格式的文件'
      return
    }
    
    // 检查文件大小（20MB限制）
    const maxSize = 20 * 1024 * 1024 // 20MB
    if (file.size > maxSize) {
      error.value = '文件大小不能超过20MB'
      return
    }
    
    selectedFile.value = file
    error.value = ''
  }
}

// 移除已选文件
const removeFile = () => {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB'
  else return (bytes / 1048576).toFixed(2) + ' MB'
}

// 文件转换为base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => {
      // 移除data URL前缀，只保留base64数据
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = error => reject(error)
  })
}

// 上传并翻译
const uploadAndTranslate = async () => {
  if (!selectedFile.value || !topic.value.trim()) {
    error.value = '请选择PDF文件并输入任务主题'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    // 转换文件为base64
    const docBase64 = await fileToBase64(selectedFile.value)
    
    // 调用翻译API
    const response = await request.post('/translate/translate_doc', {
      doc_base64: docBase64,
      topic: topic.value.trim(),
      user_id: getUserIdFromCookie()
    })
    
    // 检查响应结果
    const data = response.data
    if (data && data.code === 200) {
      // 翻译请求成功，关闭窗口
      closeModal()
      // 刷新页面
      window.location.reload()
      // 弹窗提醒成功
      ElMessage.success('翻译任务已提交')
    } else {
      error.value = '翻译请求失败：' + (data?.msg || '未知错误')
    }
  } catch (err) {
    error.value = '翻译请求失败：' + (err.message || '网络错误')
    console.error('Translate document error:', err)
  } finally {
    loading.value = false
  }
}

// 关闭窗口
const closeModal = () => {
  // 在实际应用中，这里可以通过emit事件通知父组件关闭模态框
  // 例如：defineEmits(['close']) 然后 emit('close')
  
  // 由于这是一个独立组件示例，这里简单地重置状态
  selectedFile.value = null
  topic.value = ''
  error.value = ''
  
  // 如果是在模态框中使用，可以添加关闭模态框的逻辑
  // 例如：window.close() 或调用父组件的关闭方法
}
</script>

<style scoped>
/* 基础样式 */
.translate-upload-container {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.translate-upload-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  max-width: 500px;
  margin: 0 auto;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.close-button {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.close-button:hover {
  color: #374151;
  background-color: #f3f4f6;
}

/* 卡片主体 */
.card-body {
  padding: 1.5rem;
}

/* 上传区域 */
.upload-section {
  margin-bottom: 1.5rem;
}

.upload-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.upload-area:hover:not(.has-file) {
  border-color: #667eea;
  background-color: #f9fafb;
}

.upload-area.has-file {
  border-color: #10b981;
  background-color: #f0fdf4;
}

.file-input {
  display: none;
}

.upload-placeholder {
  color: #6b7280;
}

.upload-icon {
  width: 4rem;
  height: 4rem;
  margin-bottom: 1rem;
  color: #9ca3af;
}

.upload-text {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.upload-subtext {
  font-size: 0.875rem;
  color: #9ca3af;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  text-align: left;
}

.file-icon {
  width: 2.5rem;
  height: 2.5rem;
  color: #10b981;
  margin-right: 1rem;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  margin-bottom: 0.125rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 0.75rem;
  color: #6b7280;
}

.remove-file-button {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
}

.remove-file-button:hover {
  background-color: #fee2e2;
}

/* 主题输入 */
.topic-section {
  position: relative;
}

.topic-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.topic-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.topic-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.char-count {
  position: absolute;
  right: 0.5rem;
  bottom: -1.25rem;
  font-size: 0.75rem;
  color: #9ca3af;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.cancel-button {
  padding: 0.5rem 1.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: white;
  color: #374151;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background-color: #f3f4f6;
  border-color: #9ca3af;
}

.translate-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  background-color: #667eea;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.translate-button:hover:not(:disabled) {
  background-color: #5a67d8;
}

.translate-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

/* 错误提示 */
.error-message {
  max-width: 500px;
  margin: 1rem auto 0;
  padding: 0.75rem 1rem;
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
}

.error-text {
  color: #dc2626;
  font-size: 0.875rem;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .translate-upload-card {
    margin: 0 1rem;
  }
  
  .upload-area {
    padding: 1.5rem;
  }
  
  .upload-icon {
    width: 3rem;
    height: 3rem;
  }
  
  .card-footer {
    flex-direction: column;
  }
  
  .cancel-button,
  .translate-button {
    width: 100%;
  }
}
</style>