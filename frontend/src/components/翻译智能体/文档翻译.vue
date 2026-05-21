<template>
  <div class="document-list-wrapper">
    <div class="document-list-container scientific-card">
      <!-- 头部操作区 -->
      <div class="card-header">
        <div class="title-section">
          <el-icon class="header-icon">
            <Files />
          </el-icon>
          <h2 class="card-title">文档翻译任务列表</h2>
        </div>
        <div class="header-buttons">
          <el-button type="primary" @click="showNewTaskModal = true" class="square-btn">
            <el-icon>
              <Plus />
            </el-icon>
            提交新任务
          </el-button>
          <el-button @click="fetchDocumentList" class="square-btn">
            <el-icon>
              <Refresh />
            </el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <div class="content-body">
        <div v-if="loading" class="loading-container">
          <el-icon class="loading-icon">
            <Loading />
          </el-icon>
          <p class="loading-text">加载中...</p>
        </div>

        <div v-else-if="documents.length === 0" class="empty-state">
          <el-empty description="暂无翻译文档" />
        </div>

        <div v-else class="document-table-wrapper">
          <el-table :data="documents" border stripe style="width: 100%" class="square-table"
            :header-cell-style="{ backgroundColor: '#fafbfc', color: '#303133', fontWeight: 'bold' }">
            <el-table-column prop="id" label="ID" width="80" align="center" />
            <el-table-column prop="name" label="文件名" min-width="250" show-overflow-tooltip />
            <el-table-column label="状态" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 1 ? 'success' : 'warning'" size="small" effect="plain" class="square-tag">
                  {{ row.status === 1 ? '翻译完成' : '处理中' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="300" align="center">
              <template #default="{ row }">
                <div v-if="row.status === 1" class="action-buttons">
                  <el-button type="primary" plain size="small" class="square-btn"
                    @click="downloadDocument(row.id, 'docx')" :loading="downloading.includes(row.id + '_docx')">
                    <el-icon v-if="!downloading.includes(row.id + '_docx')">
                      <Download />
                    </el-icon>
                    Word
                  </el-button>
                  <el-button type="success" plain size="small" class="square-btn"
                    @click="downloadDocument(row.id, 'pdf')" :loading="downloading.includes(row.id + '_pdf')">
                    <el-icon v-if="!downloading.includes(row.id + '_pdf')">
                      <Download />
                    </el-icon>
                    PDF
                  </el-button>
                  <el-popconfirm title="确定要删除这个文档记录吗？" @confirm="deleteDocument(row.id)" confirm-button-text="确定"
                    cancel-button-text="取消">
                    <template #reference>
                      <el-button type="danger" plain size="small" class="square-btn"
                        :loading="downloading.includes(row.id + '_delete')">
                        <el-icon v-if="!downloading.includes(row.id + '_delete')">
                          <Delete />
                        </el-icon>
                        删除
                      </el-button>
                    </template>
                  </el-popconfirm>
                </div>
                <span v-else class="no-action">处理中，请稍候...</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 错误提示 -->
      <el-alert v-if="error" :title="error" type="error" :closable="true" show-icon class="square-alert"
        @close="error = ''" />
    </div>
  </div>

  <!-- 新建翻译任务对话框 -->
  <el-dialog v-model="showNewTaskModal" title="新建翻译任务" width="800px" :close-on-click-modal="false" destroy-on-close
    class="square-dialog">
    <new_translate @close="showNewTaskModal = false" />
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Loading, Download, Delete, Files } from '@element-plus/icons-vue'
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
    const response = await axios.post('/translate/get_all_translate_doc_list', {})
    const data = response.data

    if (data && data.translate_doc_list && Array.isArray(data.translate_doc_list)) {
      documents.value = data.translate_doc_list
    } else {
      documents.value = []
      // 兼容直接返回数组的情况（视接口文档而定，这里保留原逻辑并增加宽容度）
      if (Array.isArray(data)) {
        documents.value = data
      } else {
        error.value = '获取文档列表失败，数据格式不正确'
      }
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
      const base64Data = fileType === 'pdf'
        ? data.translate_doc_detail.output_pdf_base64
        : data.translate_doc_detail.output_docx_base64

      if (!base64Data) {
        throw new Error('下载失败，服务器未返回文件数据')
      }

      const byteCharacters = atob(base64Data)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)

      const blob = new Blob([byteArray], {
        type: fileType === 'pdf'
          ? 'application/pdf'
          : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      })

      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      const doc = documents.value.find(d => d.id === docId)
      const fileName = doc ? `${doc.name}.${fileType}` : `document_${docId}.${fileType}`
      link.download = fileName

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      ElMessage.success('下载发起成功')
    } else {
      throw new Error('下载失败，文件详情获取不到')
    }
  } catch (err) {
    error.value = `下载${fileType.toUpperCase()}失败：` + (err.message || '未知错误')
    ElMessage.error(error.value)
  } finally {
    downloading.value = downloading.value.filter(key => key !== downloadKey)
  }
}

//删除文档
const deleteDocument = async (docId) => {
  const deleteKey = `${docId}_delete`
  downloading.value.push(deleteKey)
  try {
    const response = await axios.post('/translate/delete_translate_doc', {
      doc_id: docId
    })
    // 兼容多种返回格式
    if (response.data === 'ok' || response.data?.code === 200 || response.data?.msg === 'success') {
      ElMessage.success('删除成功')
      fetchDocumentList()
    } else {
      throw new Error(response.data?.msg || '删除失败')
    }
  } catch (err) {
    ElMessage.error('删除过程中出现错误：' + (err.message || '未知错误'))
  } finally {
    downloading.value = downloading.value.filter(key => key !== deleteKey)
  }
}

onMounted(() => {
  fetchDocumentList()
})
</script>

<style scoped>
.document-list-wrapper {
  padding: 16px;
  background-color: #f0f2f5;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.scientific-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 0;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafbfc;
  flex-shrink: 0;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-icon {
  font-size: 20px;
  color: #3f88f2;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-buttons {
  display: flex;
  gap: 12px;
}

.content-body {
  padding: 16px 24px;
  flex-grow: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.document-table-wrapper {
  flex-grow: 1;
  overflow: hidden;
  margin-top: 0;
}

/* 方正风格重置 */
.square-btn {
  border-radius: 0;
}

.square-tag {
  border-radius: 0;
}

.square-table :deep(.el-table__inner-wrapper) {
  border-radius: 0;
}

:deep(.el-table) {
  border-radius: 0;
  height: 100%;
}

.square-table :deep(th.el-table__cell) {
  background-color: #fafbfc !important;
}

.square-alert {
  border-radius: 0;
  margin-top: 12px;
  flex-shrink: 0;
}

:deep(.square-dialog) {
  border-radius: 0;
}

:deep(.square-dialog .el-dialog__header) {
  margin-right: 0;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 15px;
}

/* 状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
  padding: 60px 0;
  gap: 12px;
}

.loading-icon {
  font-size: 32px;
  color: #3f88f2;
}

.loading-text {
  color: #909399;
  font-size: 14px;
}

.empty-state {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.no-action {
  color: #909399;
  font-size: 13px;
  font-style: italic;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .document-list-wrapper {
    padding: 8px;
  }

  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    padding: 12px;
  }

  .header-buttons {
    width: 100%;
  }

  .header-buttons .el-button {
    flex: 1;
  }

  .content-body {
    padding: 12px;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>