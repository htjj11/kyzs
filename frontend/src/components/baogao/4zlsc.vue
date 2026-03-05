<template>
  <div class="container">
    <el-card class="upload-card">
      <!-- 上传类型切换 -->
      <div class="upload-type">
        <el-radio-group v-model="uploadType">
          <el-radio-button value="text">纯文本</el-radio-button>
          <el-radio-button value="document">文档</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 纯文本上传区域 -->
      <div v-if="uploadType === 'text'" class="upload-section">
        <el-form label-position="top">
          <el-form-item label="输入标题">
            <el-input
              v-model="textTitle"
              placeholder="请输入标题..."
              maxlength="100"
            />
          </el-form-item>
          <el-form-item label="输入文本内容">
            <el-input
              v-model="textContent"
              placeholder="请输入您的自定义知识内容..."
              maxlength="5000"
              type="textarea"
              :rows="8"
            />
            <div class="char-count">{{ textContent.length }} / 5000 字符</div>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 文档上传区域 -->
      <div v-else class="upload-section">
        <el-form label-position="top">
          <el-form-item label="文件标题">
            <el-input
              v-model="textTitle"
              placeholder="文件名将自动填充到此处，您可以修改"
              maxlength="100"
            />
          </el-form-item>
          <el-form-item label="选择文件">
            <el-upload
              ref="fileInput"
              class="upload-demo"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileSelect"
              :on-remove="removeFile"
              accept=".txt,.doc,.docx,.pdf,.md,.ppt,.pptx"
              :limit="1"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持格式：TXT, DOC, DOCX, PDF, MD, PPT, PPTX (文件大小不超过10MB)
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 操作区域 -->
      <div class="action-buttons">
        <el-select v-model="selectedTag" placeholder="选择标签" style="width: 200px">
          <el-option
            v-for="tag in userTags"
            :key="tag.id || tag"
            :label="tag.label_name"
            :value="tag.id || tag"
          />
        </el-select>
        
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!canUpload() || loading"
          @click="uploadContent"
        >
          {{ loading ? '上传中...' : '上传资料' }}
        </el-button>
        <el-button
          @click="resetForm"
          :disabled="loading"
        >
          重置
        </el-button>
      </div>
      
      <!-- 消息提示 -->
      <el-alert
        v-if="success"
        title="资料上传成功！"
        type="success"
        :closable="false"
        show-icon
      />
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        :closable="false"
        show-icon
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import request from '@/api/request';
import { getUserIdFromCookie } from '@/utils/authUtils.js';

// 将文件转换为base64编码字符串的函数
const getBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result.split(',')[1]); // 移除data URL前缀
    reader.onerror = error => reject(error);
  });
};

// 响应式数据
const uploadType = ref('text') // 'text' 或 'document'
const textContent = ref('')
const selectedFile = ref(null)
const loading = ref(false)
const error = ref('')
const success = ref(false)
const fileInput = ref(null)
const textTitle = ref('')
// 标签相关数据
const userTags = ref([])
const selectedTag = ref(null)

// 检查是否可以上传
const canUpload = () => {
  console.log('selectedTag:', selectedTag.value)
  console.log('textContent:', textContent.value)
  console.log('textTitle:', textTitle.value)
  
  // 必须选择标签
  if (!selectedTag.value) {
    console.log('没有选择标签')
    return false
  }
  
  // 检查标签是否有有效的ID或标识符
  const tagId = selectedTag.value.id || selectedTag.value
  if (!tagId) {
    console.log('标签ID无效:', selectedTag.value)
    return false
  }
  
  // 根据上传类型检查内容
  if (uploadType.value === 'text') {
    // 文本上传：至少要有标题或内容
    const hasContent = textContent.value.trim().length > 0 || textTitle.value.trim().length > 0
    console.log('文本内容检查:', hasContent)
    return hasContent
  } else {
    // 文档上传：必须选择文件
    const hasFile = selectedFile.value !== null
    console.log('文件检查:', hasFile)
    return hasFile
  }
}

// 获取标签列表
const getTagList = async () => {
  try {
    const response = await request.post('/get_setting/get_all_label', {
      user_id: getUserIdFromCookie()
    });
    
    if (response.data.code === 200) {
      userTags.value = response.data.data || [];
    } else {
      ElMessage.error(response.data.msg || '获取标签失败');
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试');
    console.error('获取标签失败:', error);
  }
}

// 处理文件选择
const handleFileSelect = (file) => {
  validateAndSetFile(file.raw)
}

// 验证并设置文件
const validateAndSetFile = (file) => {
  // 检查文件大小（这里设置最大10MB）
  const maxSize = 10 * 1024 * 1024 // 10MB
  if (file.size > maxSize) {
    error.value = '文件大小不能超过10MB'
    return
  }
  
  // 检查文件类型
  const allowedTypes = ['text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf', 'text/markdown', 'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation']
  const allowedExtensions = ['.txt', '.doc', '.docx', '.pdf', '.md', '.ppt', '.pptx']
  
  const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
  if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
    error.value = '不支持的文件格式，请上传TXT、DOC、DOCX、PDF或MD文件'
    return
  }
  
  selectedFile.value = file
  // 自动解析文件名并填充到文本框（去除扩展名）
  const fileNameWithoutExtension = file.name.substring(0, file.name.lastIndexOf('.'))
  textTitle.value = fileNameWithoutExtension
  error.value = ''
}

// 移除已选择的文件
const removeFile = () => {
  selectedFile.value = null
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 上传内容
const uploadContent = async () => {
  if (!canUpload()) {
    // 检查是否缺少标签
    if (!selectedTag.value || !selectedTag.value.id) {
      error.value = '请选择标签后再上传'
    } else {
      error.value = uploadType.value === 'text' ? '请输入文本内容' : '请选择文件'
    }
    return
  }
  
  loading.value = true
  error.value = ''
  success.value = false
  
  try {
    if (uploadType.value === 'text') {
      // 上传纯文本
      const response = await request.post('/add_to_knowledge/add_knowledge', {
        data_dict:{
          content_string:textContent.value,
          title_string:textTitle.value
        },
        label_id:selectedTag.value,
        type_id:4,
      })
      
      if (response && response.status === 200 && response.data.code === 200) {
        success.value = true
        textContent.value = ''
        textTitle.value = ''
        selectedTag.value = null
        ElMessage.success('文本上传成功')
      } else {
        error.value = '上传失败：' + (response?.data?.msg || '服务器响应异常')
      }
    } else {
      // 上传文档
      const fileExtension = selectedFile.value.name.toLowerCase().substring(selectedFile.value.name.lastIndexOf('.'))
      const fileBase64 = await getBase64(selectedFile.value)

      const response = await request.post('/add_to_knowledge/add_knowledge', {
        data_dict:{
          file_base64_string:fileBase64,
          file_extension:fileExtension,
          title_string:textTitle.value
        },
        label_id:selectedTag.value,
        type_id:5,
        user_id: getUserIdFromCookie()
      })
      
      if (response && response.status === 200 && response.data.code === 200) {
        success.value = true
        removeFile()
        selectedTag.value = null
        ElMessage.success('文档上传成功')
      } else {
        error.value = '上传失败：' + (response?.data?.msg || '服务器响应异常')
      }
    }
  } catch (err) {
    error.value = '上传失败：' + (err.message || '未知错误')
    console.error('Upload error:', err)
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  textContent.value = ''
  textTitle.value = ''
  removeFile()
  error.value = ''
  success.value = false
  selectedTag.value = null
}

// 组件挂载时加载标签列表
onMounted(() => {
  getTagList();
})
</script>

<style scoped>
.container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.upload-card {
  max-width: 800px;
  margin: 0 auto;
}

.upload-type {
  margin-bottom: 20px;
  text-align: center;
}

.upload-section {
  margin-bottom: 30px;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
}
</style>