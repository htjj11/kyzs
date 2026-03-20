<template>
  <div class="container">
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
          <el-input v-model="textTitle" placeholder="请输入标题..." maxlength="100" />
        </el-form-item>
        <el-form-item label="输入文本内容">
          <el-input v-model="textContent" placeholder="请输入您的自定义知识内容..." maxlength="5000" type="textarea" :rows="8" />
          <div class="char-count">{{ textContent.length }} / 5000 字符</div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 文档上传区域 -->
    <div v-else class="upload-section">
      <el-form label-position="top">
        <el-form-item label="选择文件（支持多文件）">
          <el-upload ref="fileInput" class="upload-demo" drag action="#" :auto-upload="false"
            :on-change="handleFileSelect" :on-remove="handleFileRemove" accept=".txt,.doc,.docx,.pdf,.md,.ppt,.pptx"
            multiple :file-list="fileList">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持格式：TXT, DOC, DOCX, PDF, MD, PPT, PPTX (单个文件不超过10MB)
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作区域 -->
    <div class="action-buttons">
      <el-select v-model="selectedTag" placeholder="选择标签" style="width: 200px">
        <el-option v-for="tag in userTags" :key="tag.id || tag" :label="tag.label_name" :value="tag.id || tag" />
      </el-select>

      <el-button type="primary" :loading="loading" :disabled="!canUpload() || loading" @click="uploadContent">
        {{ loading ? '上传中...' : '上传资料' }}
      </el-button>
      <el-button @click="resetForm" :disabled="loading">
        重置
      </el-button>
    </div>

    <!-- 消息提示 -->
    <el-alert v-if="success" title="资料上传成功！" type="success" :closable="false" show-icon />
    <el-alert v-if="error" :title="error" type="error" :closable="false" show-icon />
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
const selectedFiles = ref([]) // 多文件数组
const fileList = ref([]) // el-upload 的 file-list
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
  if (!selectedTag.value) return false
  const tagId = selectedTag.value.id || selectedTag.value
  if (!tagId) return false

  if (uploadType.value === 'text') {
    return textContent.value.trim().length > 0 || textTitle.value.trim().length > 0
  } else {
    return selectedFiles.value.length > 0
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

// 处理文件选择（多文件）
const handleFileSelect = (file) => {
  const raw = file.raw
  const maxSize = 10 * 1024 * 1024
  if (raw.size > maxSize) {
    error.value = `文件 "${raw.name}" 超过10MB，已跳过`
    // 移除超过大小的文件
    const idx = fileList.value.findIndex(f => f.uid === file.uid)
    if (idx !== -1) fileList.value.splice(idx, 1)
    return
  }

  const allowedExtensions = ['.txt', '.doc', '.docx', '.pdf', '.md', '.ppt', '.pptx']
  const fileExtension = raw.name.toLowerCase().substring(raw.name.lastIndexOf('.'))
  if (!allowedExtensions.includes(fileExtension)) {
    error.value = `文件 "${raw.name}" 格式不支持，已跳过`
    const idx = fileList.value.findIndex(f => f.uid === file.uid)
    if (idx !== -1) fileList.value.splice(idx, 1)
    return
  }

  selectedFiles.value.push(raw)
  error.value = ''
}

// 移除文件
const handleFileRemove = (file) => {
  const idx = selectedFiles.value.findIndex(f => f.name === file.raw?.name || f.name === file.name)
  if (idx !== -1) selectedFiles.value.splice(idx, 1)
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
    if (!selectedTag.value) {
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
      const response = await request.post('/add_to_knowledge/add_knowledge', {
        data_dict: {
          content_string: textContent.value,
          title_string: textTitle.value
        },
        label_id: selectedTag.value,
        type_id: 4,
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
      // 多文件上传：构建字典列表
      const dataList = []
      for (const file of selectedFiles.value) {
        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
        const fileBase64 = await getBase64(file)
        const titleStr = file.name.substring(0, file.name.lastIndexOf('.'))
        dataList.push({
          file_base64_string: fileBase64,
          file_extension: fileExtension,
          title_string: titleStr
        })
      }

      const response = await request.post('/add_to_knowledge/add_knowledge', {
        data_dict: { data: dataList },
        label_id: selectedTag.value,
        type_id: 5,
        user_id: getUserIdFromCookie()
      })

      if (response && response.status === 200 && response.data.code === 200) {
        success.value = true
        selectedFiles.value = []
        fileList.value = []
        selectedTag.value = null
        ElMessage.success(`成功上传 ${dataList.length} 个文档`)
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
  selectedFiles.value = []
  fileList.value = []
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
  width: 100%;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
  background: #f5f7fa;
  overflow: hidden;
}

.upload-type {
  margin-bottom: 20px;
  text-align: left;
}

.upload-type :deep(.el-radio-group) {
  display: inline-flex;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.upload-type :deep(.el-radio-button__inner) {
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  background: #fff;
  color: #606266;
  transition: all 0.2s ease;
}

.upload-type :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #1a5caa;
  color: #fff;
  box-shadow: none;
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