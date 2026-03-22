<template>
  <div class="new-translate-wrapper">
    <div class="scientific-card">
      <div class="card-header">
        <div class="title-section">
          <el-icon class="header-icon"><DocumentAdd /></el-icon>
          <span class="card-title">提交新翻译任务</span>
        </div>
      </div>
      
      <div class="card-body">
        <!-- PDF上传区域 -->
        <div class="form-item">
          <label class="item-label">PDF 文档上传</label>
          <div 
            class="upload-drop-zone" 
            :class="{ 'has-file': selectedFile }"
            @click="triggerFileInput"
          >
            <input 
              ref="fileInput" 
              type="file" 
              accept=".pdf" 
              class="hidden-input" 
              @change="handleFileSelect"
            >
            
            <div v-if="!selectedFile" class="upload-guide">
              <el-icon class="upload-icon"><Upload /></el-icon>
              <p class="guide-text">点击或拖拽 PDF 文件至此区域</p>
              <p class="guide-subtext">单文件限制 20MB 以内</p>
            </div>
            
            <div v-else class="selected-file-display">
              <el-icon class="file-icon"><Document /></el-icon>
              <div class="file-meta">
                <p class="file-name-text" :title="selectedFile.name">{{ selectedFile.name }}</p>
                <p class="file-size-text">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
              <el-button 
                type="danger" 
                link 
                class="remove-btn" 
                @click.stop="removeFile"
              >
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
        
        <!-- 任务主题输入 -->
        <div class="form-item">
          <label for="topic" class="item-label">任务主题 (选填)</label>
          <el-input 
            v-model="topic" 
            placeholder="如果不填写，将默认使用文件名作为任务名"
            maxlength="100"
            show-word-limit
            class="square-input"
          />
        </div>
      </div>
      
      <div class="card-actions">
        <el-button @click="closeModal" class="square-btn">取消</el-button>
        <el-button 
          type="primary" 
          :loading="loading"
          :disabled="!selectedFile || loading"
          class="square-btn main-action"
          @click="uploadAndTranslate"
        >
          开始处理翻译任务
        </el-button>
      </div>
    </div>
    
    <!-- 提示信息 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      class="square-alert"
      @close="error = ''"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentAdd, Upload, Document, Close } from '@element-plus/icons-vue'
import request from '../../api/request';
import { getUserIdFromCookie } from '@/utils/authUtils';

const emit = defineEmits(['close'])

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
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      error.value = '仅支持 PDF 格式的文件'
      return
    }
    
    // 检查文件大小（20MB限制）
    const maxSize = 20 * 1024 * 1024
    if (file.size > maxSize) {
      error.value = '文件大小不能超过 20MB'
      return
    }
    
    selectedFile.value = file
    error.value = ''
    
    // 如果主题为空，自动填入文件名（去除扩展名）
    if (!topic.value.trim()) {
      topic.value = file.name.replace(/\.[^/.]+$/, "")
    }
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
      const base64 = reader.result.split(',')[1]
      resolve(base64)
    }
    reader.onerror = error => reject(error)
  })
}

// 上传并翻译
const uploadAndTranslate = async () => {
  if (!selectedFile.value) {
    error.value = '请选择 PDF 文件'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const docBase64 = await fileToBase64(selectedFile.value)
    
    // 如果最终还没有主题，使用文件名
    const finalTopic = topic.value.trim() || selectedFile.value.name.replace(/\.[^/.]+$/, "")
    
    const response = await request.post('/translate/translate_doc', {
      doc_base64: docBase64,
      topic: finalTopic,
      user_id: getUserIdFromCookie()
    })
    
    if (response.data && (response.data.code === 200 || response.data.msg === 'success' || response.data === 'ok')) {
      ElMessage.success('翻译任务已成功提交至队列')
      closeModal()
      // 通知父组件刷新列表
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    } else {
      error.value = '任务提交失败：' + (response.data?.msg || '未知服务器错误')
    }
  } catch (err) {
    error.value = '任务提交失败：' + (err.message || '网络通讯异常')
    console.error('Translate document error:', err)
  } finally {
    loading.value = false
  }
}

// 关闭窗口
const closeModal = () => {
  selectedFile.value = null
  topic.value = ''
  error.value = ''
  emit('close')
}
</script>

<style scoped>
.new-translate-wrapper {
  padding: 8px;
}

.scientific-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 0;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafbfc;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 18px;
  color: #3f88f2;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-body {
  padding: 24px;
}

.form-item {
  margin-bottom: 24px;
}

.form-item:last-child {
  margin-bottom: 0;
}

.item-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}

.upload-drop-zone {
  border: 1px dashed #dcdfe6;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  background: #fcfdfe;
  transition: all 0.2s;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-drop-zone:hover {
  border-color: #3f88f2;
  background: #f5f9ff;
}

.upload-drop-zone.has-file {
  border-style: solid;
  border-color: #e1f3d8;
  background-color: #f0f9eb;
}

.hidden-input {
  display: none;
}

.upload-guide {
  color: #909399;
}

.upload-icon {
  font-size: 40px;
  margin-bottom: 12px;
  color: #c0c4cc;
}

.guide-text {
  font-size: 14px;
  margin-bottom: 4px;
}

.guide-subtext {
  font-size: 12px;
  color: #c0c4cc;
}

.selected-file-display {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 15px;
}

.file-icon {
  font-size: 32px;
  color: #67c23a;
}

.file-meta {
  flex: 1;
  text-align: left;
  overflow: hidden; /* 防止溢出 */
}

.file-name-text {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  /* 修复换行 bug：强制单行显示并省略 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

.file-size-text {
  font-size: 12px;
  color: #909399;
}

.remove-btn {
  font-size: 18px;
}

.square-input :deep(.el-input__wrapper) {
  border-radius: 0;
}

.card-actions {
  padding: 16px 24px;
  border-top: 1px solid #ebeef5;
  background-color: #fafbfc;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.square-btn {
  border-radius: 0;
  padding: 8px 20px;
}

.main-action {
  background-color: #3f88f2;
  border-color: #3f88f2;
}

.square-alert {
  border-radius: 0;
  margin-top: 12px;
}
</style>