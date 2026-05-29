<template>
  <div class="rag-search-container" :class="{ 'has-result': searched }">
    <div class="page-header">
      <div class="header-left">
        <el-button text type="primary" @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回个人知识库
        </el-button>
        <h2 class="page-title">个人知识库检索</h2>
      </div>
      <p class="page-desc">在当前账号绑定的 RAG 知识库中进行语义检索，匹配收藏与上传的文档片段。</p>
    </div>

    <div class="search-panel">
      <el-input
        v-model="question"
        type="textarea"
        :rows="3"
        placeholder="请输入检索问题，例如：某技术方案的核心结论、实验参数说明…"
        clearable
        resize="none"
        @keydown.enter.ctrl="handleSearch"
      />
      <div class="search-toolbar">
        <div class="search-params">
          <span class="param-label">返回条数</span>
          <el-input-number v-model="topK" :min="1" :max="30" :step="1" size="small" controls-position="right" />
          <span class="param-label">相似度阈值</span>
          <el-slider v-model="similarityThreshold" :min="0" :max="1" :step="0.05" :show-tooltip="true" style="width: 160px" />
        </div>
        <el-button type="primary" :loading="loading" @click="handleSearch">
          <el-icon><Search /></el-icon>
          开始检索
        </el-button>
      </div>
      <p class="search-hint">提示：Ctrl + Enter 快速检索</p>
    </div>

    <div v-if="searched" class="result-section">
      <div v-if="loading" class="result-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在检索个人知识库…</span>
      </div>

      <template v-else>
        <div v-if="searchError" class="result-empty">
          <el-empty :description="searchError" />
        </div>

        <template v-else-if="resultChunks.length > 0">
          <div class="result-summary">
            <span>共命中 <strong>{{ resultTotal }}</strong> 条片段</span>
            <span v-if="docAggs.length" class="doc-aggs">
              涉及文档：
              <el-tag
                v-for="doc in docAggs"
                :key="doc.doc_id"
                size="small"
                type="info"
                effect="plain"
                class="doc-tag"
              >
                {{ doc.doc_name }}（{{ doc.count }}）
              </el-tag>
            </span>
          </div>

          <div class="chunk-list">
            <el-card
              v-for="(chunk, index) in resultChunks"
              :key="chunk.id || index"
              class="chunk-card"
              shadow="hover"
            >
              <div class="chunk-header">
                <span class="chunk-rank">#{{ index + 1 }}</span>
                <span class="chunk-doc">{{ getChunkDocName(chunk) }}</span>
                <el-tag size="small" type="success" effect="plain">
                  相似度 {{ formatSimilarity(chunk.similarity) }}
                </el-tag>
              </div>
              <div
                class="chunk-content"
                v-html="chunk.highlight || escapeHtml(chunk.content || '')"
              />
              <div v-if="hasExtraScores(chunk)" class="chunk-scores">
                <span>向量 {{ formatSimilarity(chunk.vector_similarity) }}</span>
                <span>关键词 {{ formatSimilarity(chunk.term_similarity) }}</span>
              </div>
            </el-card>
          </div>
        </template>

        <div v-else class="result-empty">
          <el-empty description="未检索到相关内容，可尝试降低相似度阈值或更换问法" />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Search, Loading } from '@element-plus/icons-vue'
import request from '@/api/request'
import { getUserIdFromCookie } from '@/utils/authUtils'

const router = useRouter()

const question = ref('')
const topK = ref(10)
const similarityThreshold = ref(0.2)
const loading = ref(false)
const searched = ref(false)
const searchError = ref('')
const resultChunks = ref([])
const docAggs = ref([])
const resultTotal = ref(0)

const goBack = () => {
  router.push('/zskck')
}

const escapeHtml = (text) => {
  if (!text) return ''
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/\n/g, '<br>')
}

const formatSimilarity = (value) => {
  const num = Number(value)
  if (Number.isNaN(num)) return '-'
  return `${(num * 100).toFixed(1)}%`
}

const getChunkDocName = (chunk) => {
  return (
    chunk.document_keyword ||
    chunk.document_name ||
    chunk.doc_name ||
    chunk.docnm_kwd ||
    '未知文档'
  )
}

const hasExtraScores = (chunk) => {
  return chunk.vector_similarity != null || chunk.term_similarity != null
}

const normalizeChunks = (data) => {
  if (!data) return []
  const raw = data.chunks
  if (Array.isArray(raw)) return raw
  if (raw && typeof raw === 'object') return Object.values(raw)
  return []
}

const handleSearch = async () => {
  const q = question.value.trim()
  if (!q) {
    ElMessage.warning('请输入检索问题')
    return
  }

  const userId = getUserIdFromCookie()
  if (!userId) {
    ElMessage.error('未登录，请先登录')
    router.push('/login')
    return
  }

  searched.value = true
  loading.value = true
  searchError.value = ''
  resultChunks.value = []
  docAggs.value = []
  resultTotal.value = 0

  try {
    const response = await request.post('/personal_knowledgebase/rag_search', {
      user_id: userId,
      question: q,
      top_k: topK.value,
      similarity_threshold: similarityThreshold.value
    })

    if (response.data?.code === 200 && response.data.data) {
      const data = response.data.data
      resultChunks.value = normalizeChunks(data)
      docAggs.value = Array.isArray(data.doc_aggs) ? data.doc_aggs : []
      resultTotal.value = data.total ?? resultChunks.value.length
      if (resultChunks.value.length === 0) {
        ElMessage.info('未检索到匹配片段')
      } else {
        ElMessage.success(`检索完成，共 ${resultTotal.value} 条`)
      }
    } else {
      searchError.value = response.data?.msg || '检索失败'
      ElMessage.error(searchError.value)
    }
  } catch (error) {
    console.error('个人知识库检索失败:', error)
    searchError.value = error.message || '检索请求失败'
    ElMessage.error(searchError.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.rag-search-container {
  height: calc(100vh - 56px);
  padding: 16px 20px 24px;
  box-sizing: border-box;
  background: #f4f6f8;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.page-desc {
  margin: 8px 0 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

.search-panel {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.search-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.search-params {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.param-label {
  font-size: 13px;
  color: #606266;
  white-space: nowrap;
}

.search-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: #c0c4cc;
}

.result-section {
  margin-top: 16px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.result-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 48px;
  color: #606266;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.result-summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #ecf5ff;
  border: 1px solid #d9ecff;
  border-radius: 4px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #606266;
}

.doc-aggs {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.doc-tag {
  margin: 0;
}

.chunk-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chunk-card {
  border-radius: 4px;
}

.chunk-card :deep(.el-card__body) {
  padding: 14px 16px;
}

.chunk-header {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.chunk-rank {
  font-weight: 700;
  color: #409eff;
  font-size: 14px;
}

.chunk-doc {
  flex: 1;
  min-width: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chunk-content {
  font-size: 14px;
  line-height: 1.75;
  color: #303133;
  word-break: break-word;
}

.chunk-content :deep(em) {
  font-style: normal;
  background: #fff3cd;
  color: #e6a23c;
  padding: 0 2px;
  border-radius: 2px;
}

.chunk-scores {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed #ebeef5;
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 16px;
}

.result-empty {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 24px;
}
</style>
