<template>
  <div class="literature-container" :class="{ 'has-result': searched }">
    <!-- 加载遮罩 -->
    <transition name="fade">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span class="loading-text">{{ loadingText }}</span>
      </div>
    </transition>

    <!-- 搜索区域：未搜索时居中，搜索后收缩到顶部 -->
    <div class="search-area">
      <div class="search-form">
        <div class="form-row">
          <div class="form-item">
            <label>关键词：</label>
            <el-input v-model="keywords" placeholder="多个关键词用逗号分隔" style="width: 300px" clearable
              @keyup.enter="doSearch" />
          </div>
          <div class="form-item">
            <label>年份：</label>
            <el-input-number v-model="startYear" :min="1800" :max="currentYear" placeholder="起始"
              controls-position="right" style="width:120px" />
            <span class="year-sep">—</span>
            <el-input-number v-model="endYear" :min="1800" :max="currentYear" placeholder="结束" controls-position="right"
              style="width:120px" />
          </div>
          <div class="form-actions">
            <el-button type="primary" :loading="loading" @click="doSearch">搜索</el-button>
            <el-checkbox v-model="useTranslation">中转英搜索</el-checkbox>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果区域：仅搜索后显示 -->
    <transition name="result-fade">
      <div v-if="searched" class="data-section">
        <el-table v-loading="loading" :data="list" border stripe style="width:100%">
          <el-table-column label="来源" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="sourceTagType(row.source)" size="small" effect="dark">{{ row.source }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="250" show-overflow-tooltip />
          <el-table-column prop="keywords" label="关键词" min-width="180" show-overflow-tooltip />
          <el-table-column prop="year" label="年份" width="80" />
          <el-table-column prop="abstract" label="摘要" min-width="300" show-overflow-tooltip />
          <el-table-column prop="doi" label="DOI" width="160" show-overflow-tooltip />
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.download_url" type="warning" size="small" @click="openUrl(row.download_url)"
                style="margin-right:4px">下载</el-button>
              <span v-if="row.is_collected === 1" class="collected-text">已收藏</span>
              <el-button v-else type="primary" size="small" @click="handleCollect(row)">收藏</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!loading && searched && list.length === 0 && page === 1" description="暂无相关文献" />

        <div class="pagination-box" v-if="searched">
          <el-button :disabled="page <= 1" size="small" @click="page--; fetchData()">上一页</el-button>
          <span class="page-info">第 {{ page }} 页</span>
          <el-button :disabled="list.length === 0" size="small" @click="page++; fetchData()">下一页</el-button>
          <span class="page-sep">|</span>
          <span class="page-label">每页</span>
          <el-select v-model="pageSize" size="small" style="width:90px" @change="onPageSizeChange">
            <el-option :value="10" label="10 条" />
            <el-option :value="20" label="20 条" />
            <el-option :value="50" label="50 条" />
          </el-select>
        </div>
      </div>
    </transition>

    <GetLabelList v-model:visible="showLabelDialog" @select-label="handleLabelConfirm" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import request from '@/api/request.js'
import { ElMessage } from 'element-plus'
import { getUserIdFromCookie } from '@/utils/authUtils.js'
import GetLabelList from '@/components/small/get_label_list.vue'

const currentYear = new Date().getFullYear()
const keywords = ref('')
const startYear = ref(currentYear - 5)
const endYear = ref(currentYear)
const loading = ref(false)
const loadingText = ref('正在检索文献…')
const useTranslation = ref(false)
const searched = ref(false)

const list = ref([])
const page = ref(1)
const pageSize = ref(20)

let activeKeywords = ''

// =================== 翻译 ===================
const translateKeyword = async (kw) => {
  try {
    const resp = await request.post('/get_source/translate_keyword', { keyword: kw })
    if (resp.data.code === 200) {
      const result = resp.data.data?.translate_result || kw
      return typeof result === 'string' ? result : String(result)
    }
    return kw
  } catch { return kw }
}

// =================== 搜索 ===================
const doSearch = async () => {
  if (!keywords.value.trim()) { ElMessage.warning('请输入搜索关键词'); return }
  let kw = keywords.value
  if (useTranslation.value) {
    loadingText.value = '正在翻译关键词…'
    loading.value = true
    const arr = kw.split(',').map(k => k.trim()).filter(Boolean)
    const translated = []
    for (const k of arr) translated.push(await translateKeyword(k))
    kw = translated.join(',')
    keywords.value = kw
    loading.value = false
  }
  activeKeywords = kw
  page.value = 1
  fetchData()
}

const fetchData = async () => {
  if (!activeKeywords) return
  loadingText.value = '正在检索文献…'
  loading.value = true
  searched.value = true
  try {
    const resp = await request.post('/get_source/search_all_articles', {
      keywords: activeKeywords,
      start_year: startYear.value || null,
      end_year: endYear.value || null,
      page: page.value,
      size: pageSize.value,
      user_id: getUserIdFromCookie() || 1,
    })
    if (resp.data.code === 200) {
      list.value = resp.data.data || []
    } else {
      ElMessage.error(resp.data.msg || '搜索失败')
    }
  } catch { ElMessage.error('网络错误') }
  finally { loading.value = false }
}

const onPageSizeChange = () => {
  page.value = 1
  fetchData()
}

// =================== 来源标签颜色 ===================
const sourceTagType = (source) => {
  if (source === 'OilLink') return ''
  if (source === '聚合') return 'success'
  if (source === '万方') return 'warning'
  return 'info'
}

// =================== 收藏 ===================
const showLabelDialog = ref(false)
const pendingCollect = ref(null)

const handleCollect = (row) => {
  pendingCollect.value = {
    row, type_id: 1,
    dataMapper: (r) => ({ title: r.title, abstract: r.abstract, keywords: r.keywords, doi: r.doi })
  }
  showLabelDialog.value = true
}

const handleLabelConfirm = async ({ label_id }) => {
  if (!pendingCollect.value || !label_id) return
  const { row, type_id, dataMapper } = pendingCollect.value
  try {
    const resp = await request.post('/add_to_knowledge/add_knowledge', {
      data_dict: dataMapper ? dataMapper(row) : row,
      label_id, type_id,
      user_id: getUserIdFromCookie() || 1,
    })
    if (resp.data.code === 200) {
      ElMessage.success('收藏成功'); row.is_collected = 1
    } else { ElMessage.error(resp.data.msg || '收藏失败') }
  } catch { ElMessage.error('收藏失败') }
  finally { pendingCollect.value = null }
}

const openUrl = (url) => {
  if (url) window.open(url.replace(/`/g, '').trim(), '_blank')
}
</script>

<style scoped>
/* ===== 基础容器 ===== */
.literature-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* 搜索前：垂直居中 */
  height: 100%;
  padding: 24px 24px;
  box-sizing: border-box;
  background: #f4f6f8;
  overflow: hidden;
  transition: justify-content 0.4s ease, padding 0.4s ease;
}

/* 有结果时：顶部对齐 */
.literature-container.has-result {
  justify-content: flex-start;
  padding: 12px 16px;
}

/* ===== 搜索区域 ===== */
.search-area {
  width: 100%;
  max-width: 900px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.35s ease;
}

/* 有结果时搜索区域靠左对齐 */
.has-result .search-area {
  align-items: flex-start;
  max-width: 100%;
  margin-bottom: 10px;
}

/* ===== 居中时的大标题 ===== */
.hero-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  color: #1a2b4a;
  margin-bottom: 28px;
  letter-spacing: 1px;
}

.hero-icon {
  font-size: 36px;
}

/* ===== 搜索表单 ===== */
.search-form {
  width: 100%;
  background: #fff;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, .10);
  transition: box-shadow 0.3s ease, border-radius 0.3s ease;
}

.has-result .search-form {
  box-shadow: 0 1px 4px rgba(0, 0, 0, .06);
  border-radius: 6px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.form-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.form-item label {
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.form-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}

.year-sep {
  margin: 0 4px;
  color: #999;
}

/* ===== 数据区 ===== */
.data-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  padding: 12px 16px;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, .06);
  overflow: hidden;
  min-height: 0;
  width: 100%;
}

:deep(.el-table) {
  flex: 1;
  height: 0 !important;
}

:deep(.el-table__body-wrapper) {
  overflow-y: auto;
}

.collected-text {
  color: #67c23a;
  font-size: 13px;
}

/* ===== 分页 ===== */
.pagination-box {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  justify-content: center;
}

.page-info {
  font-size: 14px;
  color: #606266;
  min-width: 60px;
  text-align: center;
}

.page-sep {
  color: #ddd;
}

.page-label {
  font-size: 13px;
  color: #909399;
}

/* ===== 加载遮罩 ===== */
.loading-overlay {
  position: absolute;
  inset: 0;
  z-index: 100;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: rgba(244, 246, 248, 0.88);
  backdrop-filter: blur(2px);
}

.loading-spinner {
  width: 44px;
  height: 44px;
  border: 4px solid #d0dff0;
  border-top-color: #1a5caa;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-text {
  font-size: 14px;
  color: #1a2b4a;
  font-weight: 500;
  letter-spacing: 0.5px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ===== 过渡动画 ===== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.title-fade-enter-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.title-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.title-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.title-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.result-fade-enter-active {
  transition: opacity 0.35s ease 0.1s, transform 0.35s ease 0.1s;
}

.result-fade-leave-active {
  transition: opacity 0.2s ease;
}

.result-fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.result-fade-leave-to {
  opacity: 0;
}
</style>
