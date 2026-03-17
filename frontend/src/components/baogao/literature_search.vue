<template>
  <div class="literature-container">
    <h3 class="page-title">文献检索</h3>
    <div class="search-form">
      <div class="form-row">
        <div class="form-item">
          <label>关键词：</label>
          <el-input v-model="keywords" placeholder="多个关键词用逗号分隔" style="width: 300px" clearable @keyup.enter="doSearch" />
        </div>
        <div class="form-item">
          <label>年份：</label>
          <el-input-number v-model="startYear" :min="1800" :max="currentYear" placeholder="起始" controls-position="right" style="width:120px" />
          <span class="year-sep">—</span>
          <el-input-number v-model="endYear" :min="1800" :max="currentYear" placeholder="结束" controls-position="right" style="width:120px" />
        </div>
        <div class="form-actions">
          <el-button type="primary" :loading="loading" @click="doSearch">搜索</el-button>
          <el-checkbox v-model="useTranslation">中转英搜索</el-checkbox>
        </div>
      </div>
    </div>

    <div class="data-section">
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
            <el-button v-if="row.download_url" type="warning" size="small" @click="openUrl(row.download_url)" style="margin-right:4px">下载</el-button>
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
        <span class="page-label">每源</span>
        <el-select v-model="pageSize" size="small" style="width:90px" @change="onPageSizeChange">
          <el-option :value="10" label="10 条" />
          <el-option :value="20" label="20 条" />
          <el-option :value="50" label="50 条" />
        </el-select>
      </div>
    </div>

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
const startYear = ref(null)
const endYear = ref(null)
const loading = ref(false)
const useTranslation = ref(false)
const searched = ref(false)

const list = ref([])
const page = ref(1)
const pageSize = ref(20)

let activeKeywords = ''

// =================== 翻译 ===================
const translateKeyword = async (kw) => {
  try {
    const resp = await request.post('/get_from_oilink/translate_keyword', { keyword: kw })
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
    const arr = kw.split(',').map(k => k.trim()).filter(Boolean)
    const translated = []
    for (const k of arr) translated.push(await translateKeyword(k))
    kw = translated.join(',')
    keywords.value = kw
  }
  activeKeywords = kw
  page.value = 1
  fetchData()
}

const fetchData = async () => {
  if (!activeKeywords) return
  loading.value = true
  searched.value = true
  try {
    const resp = await request.post('/get_from_oilink/search_all_articles', {
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
.literature-container { padding: 20px; min-height: 100vh; background: #f5f7fa; }
.page-title { font-size: 20px; font-weight: bold; color: #333; margin-bottom: 16px; }
.search-form { background: #fff; padding: 16px 20px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.form-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.form-item { display: flex; align-items: center; gap: 6px; }
.form-item label { font-weight: 500; color: #606266; white-space: nowrap; }
.form-actions { margin-left: auto; display: flex; gap: 8px; align-items: center; }
.year-sep { margin: 0 4px; color: #999; }
.data-section { background: #fff; padding: 16px 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.collected-text { color: #67c23a; font-size: 13px; }
.pagination-box { display: flex; align-items: center; gap: 12px; margin-top: 16px; justify-content: center; }
.page-info { font-size: 14px; color: #606266; min-width: 60px; text-align: center; }
.page-sep { color: #ddd; }
.page-label { font-size: 13px; color: #909399; }
</style>
