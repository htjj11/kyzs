<template>
  <div class="document-list-container">
    <div class="max-w-4xl mx-auto">
 
      
      <!-- 文档列表标题和操作按钮 -->
      <div class="card-header">
        <h2 class="card-title">文档列表</h2>
        <div class="header-buttons">
          <el-button type="primary" @click="showNewTaskModal = true" class="new-task-button">
            <el-icon><Plus /></el-icon>
            新建翻译任务
          </el-button>
          <el-button type="success" @click="fetchDocumentList" class="refresh-button">
            <el-icon><Refresh /></el-icon>
            刷新列表
          </el-button>
        </div>
      </div>
        
        <div v-if="loading" class="loading-container">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <p class="loading-text">加载中...</p>
        </div>
        
        <div v-else-if="documents.length === 0" class="empty-state">
          <el-empty description="暂无翻译文档" />
        </div>
        
        <div v-else class="document-table">
          <el-table 
            :data="documents" 
            stripe 
            style="width: 100%"
            :header-cell-style="{ backgroundColor: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column prop="id" label="文档ID" width="120" align="center" />
            <el-table-column prop="name" label="文档名称" min-width="200" />
            <el-table-column label="状态" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 1 ? 'success' : 'warning'" size="small">
                  {{ row.status === 1 ? '完成' : '未完成' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280" align="center">
              <template #default="{ row }">
                <div v-if="row.status === 1" class="action-buttons">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="downloadDocument(row.id, 'docx')"
                    :loading="downloading.includes(row.id + '_docx')"
                  >
                    <el-icon v-if="!downloading.includes(row.id + '_docx')"><Download /></el-icon>
                    {{ downloading.includes(row.id + '_docx') ? '下载中...' : '下载DOCX' }}
                  </el-button>
                  <el-button 
                    type="success" 
                    size="small" 
                    @click="downloadDocument(row.id, 'pdf')"
                    :loading="downloading.includes(row.id + '_pdf')"
                  >
                    <el-icon v-if="!downloading.includes(row.id + '_pdf')"><Download /></el-icon>
                    {{ downloading.includes(row.id + '_pdf') ? '下载中...' : '下载PDF' }}
                  </el-button>
                  <el-popconfirm
                    title="确定要删除这个文档记录吗？"
                    @confirm="deleteDocument(row.id)"
                    confirm-button-text="确定"
                    cancel-button-text="取消"
                  >
                    <template #reference>
                      <el-button 
                        type="danger" 
                        size="small"
                        :loading="downloading.includes(row.id + '_delete')"
                      >
                        <el-icon v-if="!downloading.includes(row.id + '_delete')"><Delete /></el-icon>
                        删除记录
                      </el-button>
                    </template>
                  </el-popconfirm>
                </div>
                <span v-else class="no-action">无操作</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      
      <!-- 错误提示 -->
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        :closable="false"
        show-icon
        class="error-alert"
      />
    </div>
  </div>

  <!-- 新建翻译任务模态框 -->
  <el-dialog
    v-model="showNewTaskModal"
    title="新建翻译任务"
    width="80%"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <new_translate @close="showNewTaskModal = false" />
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Loading, Download, Delete } from '@element-plus/icons-vue'
import axios from "@/api/request.js";
import new_translate from '@/components/small/new_translate.vue'

// 响应式数据
const documents = ref([])
const loading = ref(false)
const error = ref('')
const downloading = ref([])
const showNewTaskModal = ref(false)

// 获取文档列表
const fetchDocumentList = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await axios.post('/translate/get_all_translate_doc_list', {
    })
    const data = response.data
    
    if (data && data.translate_doc_list && Array.isArray(data.translate_doc_list)) {
      documents.value = data.translate_doc_list
    } else {
      documents.value = []
      error.value = '获取文档列表失败，数据格式不正确'
    }
  } catch (err) {
    documents.value = []
    error.value = '获取文档列表失败：' + (err.message || '未知错误')
    console.error('Fetch document list error:', err)
  } finally {
    loading.value = false
  }
}

// 下载文档
const downloadDocument = async (docId, fileType) => {
  const downloadKey = `${docId}_${fileType}`
  downloading.value.push(downloadKey)
  error.value = ''
  
  try {
    const response = await axios.post('/translate/get_translate_doc_detail', {
      doc_id: docId
    })
    
    const data = response.data
    if (data && data.translate_doc_detail) {
      // 根据 fileType 获取对应的 base64 字段
      const base64Data = fileType === 'pdf'
        ? data.translate_doc_detail.output_pdf_base64
        : data.translate_doc_detail.output_docx_base64

      if (!base64Data) {
        error.value = '下载失败，文件数据不存在'
        return
      }

      // 解码 base64 数据
      const byteCharacters = atob(base64Data)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)

      // 创建 Blob 对象
      const blob = new Blob([byteArray], {
        type: fileType === 'pdf'
          ? 'application/pdf'
          : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      })

      // 创建下载链接
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // 查找对应的文档名称
      const doc = documents.value.find(d => d.id === docId)
      const fileName = doc ? `${doc.name}.${fileType}` : `document_${docId}.${fileType}`
      link.download = fileName

      // 触发下载
      document.body.appendChild(link)
      link.click()

      // 清理
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } else {
      error.value = '下载失败，文件数据不存在'
    }
  } catch (err) {
    error.value = `下载${fileType.toUpperCase()}失败：` + (err.message || '未知错误')
    console.error(`Download ${fileType} error:`, err)
  } finally {
    downloading.value = downloading.value.filter(key => key !== downloadKey)
  }
}

//删除文档
const deleteDocument = async (docId) => {
  try {
    const response = await axios.post('/translate/delete_translate_doc', {  
      doc_id: docId
    })
    if (response==='ok') {
      ElMessage.success('删除成功')
      fetchDocumentList()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (err) {
    ElMessage.error('删除失败')
    console.error('Delete document error:', err)
  }
}

// 页面加载时获取文档列表
onMounted(() => {
  fetchDocumentList()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.header-buttons {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.new-task-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #10b981;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s ease;
}

.new-task-button:hover {
  background-color: #059669;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s ease;
}


.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 56rem;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.modal-close:hover {
  color: #111827;
  background-color: #f3f4f6;
}

.modal-body {
  padding: 1rem;
  overflow-y: auto;
  flex: 1;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-buttons {
    flex-direction: column;
    gap: 0.5rem;
    width: 100%;
  }
  
  .new-task-button,
  .refresh-button {
    width: 100%;
    justify-content: center;
  }

}

/* 基础样式 */
.document-list-container {
  height: 100%;
  padding: 2rem 1rem;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.max-w-4xl {
  margin: 0 auto;
}

/* 标题样式 */
.text-center {
  text-align: center;
  margin-bottom: 2rem;
}

.text-3xl {
  font-size: 1.875rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

.text-gray-100 {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1rem;
}

/* 卡片头部样式 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.refresh-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s ease;
}

.refresh-button:hover {
  background-color: #5a67d8;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-icon {
  font-size: 2rem;
  color: #409eff;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: #6b7280;
  font-size: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  color: #6b7280;
}

/* Element Plus 组件样式优化 */
.document-table {
  overflow-x: auto;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.no-action {
  color: #909399;
  font-style: italic;
}

/* 错误提示 */
.error-alert {
  margin-top: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>