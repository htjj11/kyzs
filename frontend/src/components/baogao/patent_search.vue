<template>
  <div class="patent-container">
    <div class="search-form">
      <div class="form-row">
        <div class="form-item">
          <label>关键词：</label>
          <el-tooltip content="专利使用英文搜索结果更多哦" placement="top">
            <el-button type="text" icon="InfoFilled" class="info-tooltip" style="margin-left:4px;" />
          </el-tooltip>
          <el-input v-model="keywords" placeholder="多个关键词用逗号分隔" style="width:300px" clearable @keyup.enter="doSearch" />
        </div>
        <div class="form-item">
          <label>年份：</label>
          <el-input-number v-model="startYear" :min="1800" :max="currentYear" placeholder="起始" controls-position="right" style="width:120px" />
          <span class="year-sep">—</span>
          <el-input-number v-model="endYear" :min="1800" :max="currentYear" placeholder="结束" controls-position="right" style="width:120px" />
        </div>
        <div class="form-actions">
          <el-button type="primary" :loading="loading" @click="doSearch">搜索</el-button>
          <el-checkbox v-model="useTranslation">中译英搜索</el-checkbox>
        </div>
      </div>
    </div>

    <div class="data-section">
      <el-table v-loading="loading" :data="list" border stripe style="width:100%">
        <el-table-column label="来源" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.source === '万方' ? 'warning' : ''" size="small" effect="dark">{{ row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="专利名称" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <a href="javascript:void(0)" @click="viewDetail(row)" class="title-link">{{ row.title }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="applicant" label="申请人" min-width="140" show-overflow-tooltip />
        <el-table-column prop="inventor" label="发明人" min-width="120" show-overflow-tooltip />
        <el-table-column prop="app_date" label="申请日" width="120" />
        <el-table-column prop="pub_date" label="公开日" width="120" />
        <el-table-column prop="abstract" label="摘要" min-width="260" show-overflow-tooltip />
        <el-table-column label="操作" width="130" fixed="right">
          <template #default="{ row }">
            <span v-if="row.is_collected === 1" class="collected-text">已收藏</span>
            <el-button v-else type="primary" size="small" @click="handleCollect(row)">收藏</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && searched && list.length === 0 && page === 1" description="暂无相关专利" />

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

    <!-- 专利详情弹窗 -->
    <el-dialog v-model="detailVisible" title="专利详情" width="85%">
      <div class="patent-detail" v-if="currentDetail">
        <div class="detail-row" v-for="item in detailFields" :key="item.label">
          <div class="detail-label">{{ item.label }}:</div>
          <div class="detail-value" style="white-space:pre-wrap">{{ item.value }}</div>
        </div>
      </div>
      <template #footer><el-button @click="detailVisible = false">关闭</el-button></template>
    </el-dialog>

    <GetLabelList v-model:visible="showLabelDialog" @select-label="handleLabelConfirm" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import request from '@/api/request.js'
import { ElMessage } from 'element-plus'
import { getUserIdFromCookie } from '@/utils/authUtils.js'
import GetLabelList from '@/components/small/get_label_list.vue'
import { InfoFilled } from '@element-plus/icons-vue'

const currentYear = new Date().getFullYear()
const keywords = ref('')
const startYear = ref(currentYear - 5)
const endYear = ref(currentYear)
const loading = ref(false)
const loadingText = ref('正在检索专利…')
const useTranslation = ref(false)
const searched = ref(false)

const list = ref([])
const page = ref(1)
const pageSize = ref(20)

// =================== 搜索 ===================
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
  page.value = 1
  fetchData()
}

const fetchData = async () => {
  loading.value = true
  searched.value = true
  try {
    const resp = await request.post('/get_source/search_all_patents', {
      keywords: keywords.value.trim(),
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

// =================== 详情弹窗 ===================
const detailVisible = ref(false)
const currentDetail = ref(null)
const detailFields = computed(() => {
  const d = currentDetail.value
  if (!d) return []
  return [
    { label: '来源', value: d.source },
    { label: '专利名称', value: d.title },
    { label: '申请人', value: d.applicant },
    { label: '发明人', value: d.inventor },
    { label: '申请号', value: d.app_num },
    { label: '申请日', value: d.app_date },
    { label: '公开号', value: d.pub_num },
    { label: '公开日', value: d.pub_date },
    { label: '国家', value: d.country },
    { label: '摘要', value: d.abstract },
  ]
})
const viewDetail = (row) => { currentDetail.value = { ...row }; detailVisible.value = true }

// =================== 收藏 ===================
const showLabelDialog = ref(false)
const pendingCollect = ref(null)

const fmtDate = (s) => {
  if (!s) return ''
  const str = String(s)
  if (/^\d{4}-\d{2}-\d{2}$/.test(str)) return str + 'T00:00:00'
  return str
}

const handleCollect = (row) => {
  let dataMapper
  if (row.source === 'OilLink') {
    dataMapper = (r) => r._raw
  } else {
    dataMapper = (r) => ({
      id: r.pub_num || '', title: r.title || '', abstract: r.abstract || '',
      country: r.country || 'CN', app_num: r.app_num || '',
      app_date: fmtDate(r.app_date), pub_num: r.pub_num || '',
      pub_date: fmtDate(r.pub_date), pub_kind: '', applicant: r.applicant || '',
    })
  }
  pendingCollect.value = { row, type_id: 2, dataMapper }
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
</script>

<style scoped>
/* Loading overlay */
.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(2px);
  z-index: 10;
}
.loading-spinner {
  width: 44px;
  height: 44px;
  border: 4px solid #ddd;
  border-top-color: #1a2b4a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
.loading-text {
  margin-top: 8px;
  font-size: 14px;
  color: #1a2b4a;
}
@keyframes spin { to { transform: rotate(360deg); } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.patent-container {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px 16px;
  box-sizing: border-box;
  background: #f4f6f8;
  overflow: hidden;
}

/* 搜索栏：固定高度 */
.search-form {
  flex-shrink: 0;
  background: #fff;
  padding: 10px 16px;
  border-radius: 6px;
  margin-bottom: 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
}

.form-row { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.form-item { display: flex; align-items: center; gap: 6px; }
.form-item label { font-weight: 500; color: #606266; white-space: nowrap; }
.form-actions { margin-left: auto; display: flex; gap: 8px; }
.year-sep { margin: 0 4px; color: #999; }

/* 数据区：撑满剩余高度 */
.data-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  padding: 12px 16px;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
  overflow: hidden;
  min-height: 0;
}

/* el-table 填满 data-section 剩余空间 */
:deep(.el-table) {
  flex: 1;
  height: 0 !important;
}
:deep(.el-table__body-wrapper) { overflow-y: auto; }

.collected-text { color: #67c23a; font-size: 13px; }
.title-link { color: #409eff; cursor: pointer; }

/* 分页栏 */
.pagination-box {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  justify-content: center;
}
.page-info { font-size: 14px; color: #606266; min-width: 60px; text-align: center; }
.page-sep { color: #ddd; }
.page-label { font-size: 13px; color: #909399; }

.patent-detail { max-height: 70vh; overflow-y: auto; }
.detail-row { display: flex; margin-bottom: 14px; }
.detail-label { width: 110px; font-weight: bold; color: #606266; flex-shrink: 0; }
.detail-value { flex: 1; color: #303133; }
</style>
