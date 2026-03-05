<template>
  <div class="article-wanfang-container">
    <!-- 搜索区域 -->
    <div class="search-section">
      <div class="search-form">
        <el-form ref="searchFormRef" :model="searchForm" label-width="80px" inline>
          <el-form-item label="关键词：">
            <el-input
              v-model="searchForm.keywords"
              placeholder="请输入关键词，多个关键词用逗号分隔"
              clearable
              style="width: 400px"
            />
          </el-form-item>
          <el-form-item label="年份：">
            <el-input-number
              v-model="searchForm.year"
              :min="2000"
              :max="new Date().getFullYear()"
              placeholder="请输入年份"
              style="width: 120px"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              @click="searchArticles"
              :loading="loading"
              icon="Search"
            >
              搜索
            </el-button>
            <el-button
              @click="resetForm"
              :loading="loading"
            >
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 结果展示区域 -->
    <div class="results-section">
      <!-- 结果统计 -->
      <div class="results-stats" v-if="!loading && total > 0">
        <span>共找到 {{ total }} 条结果</span>
      </div>

      <!-- 文章列表表格 -->
      <el-table
        v-loading="loading"
        :data="articleList"
        style="width: 100%"
        border
        stripe
        v-if="articleList.length > 0"
      >
        <el-table-column prop="标题" label="标题" min-width="300">
          <template #default="scope">
            <el-popover
              placement="top"
              width="600"
              trigger="hover"
            >
              <template #reference>
                <span class="title-text">{{ scope.row.标题 }}</span>
              </template>
              <div class="title-popover">
                {{ scope.row.标题 }}
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="关键词" label="关键词" min-width="200">
          <template #default="scope">
            <el-tag
              v-for="(keyword, index) in scope.row.关键词.split(',')"
              :key="index"
              size="small"
              style="margin-right: 5px; margin-bottom: 5px;"
            >
              {{ keyword.trim() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="摘要" label="摘要" min-width="400">
          <template #default="scope">
            <el-popover
              placement="top"
              width="800"
              trigger="hover"
            >
              <template #reference>
                <span class="abstract-text">{{ truncateText(scope.row.摘要, 100) }}</span>
              </template>
              <div class="abstract-popover">
                {{ scope.row.摘要 }}
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="发表时间" label="发表时间" width="100" align="center" />
      <el-table-column prop="DOI" label="DOI" min-width="150" />
      <!-- 操作列 -->
      <el-table-column label="操作" width="150" align="center">
        <template #default="scope">
          <el-button 
            v-if="scope.row.is_collected === 0"
            type="primary" 
            size="small" 
            @click="handleAddToKnowledgeBase(scope.row)"
          >
            添加到知识库
          </el-button>
          <el-button 
            v-else
            type="default" 
            size="small" 
            disabled
          >
            已收藏
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 标签选择组件 -->
    <GetLabelList 
      v-model:visible="labelDialogVisible" 
      @selectLabel="handleLabelSelect"
    />

      <!-- 空状态 -->
      <div v-if="!loading && articleList.length === 0" class="empty-state">
        <el-empty description="暂无相关文献" />
      </div>

      <!-- 分页控件 -->
      <div v-if="!loading && Number(total) > 0" class="pagination-container">
        <!-- 添加调试信息 -->
        <div v-if="false">
          <p>调试信息：</p>
          <p>total: {{ total }}</p>
          <p>pageSize: {{ pageSize }}</p>
          <p>currentPage: {{ currentPage }}</p>
          <p>totalPages: {{ totalPages }}</p>
        </div>
        
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :pager-count="10"
          background
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      <!-- 分页不显示时的调试提示 -->
      <div v-else-if="!loading" style="text-align: center; color: #909399; margin-top: 20px;">
        <p>分页组件未显示 - 调试信息：total={{ total }}, loading={{ loading }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/request'
import GetLabelList from '@/components/small/get_label_list.vue'

// 搜索表单引用
const searchFormRef = ref()
// 搜索表单数据
const searchForm = reactive({
  keywords: '',
  year: ''
})
// 加载状态
const loading = ref(false)
// 文章列表数据
const articleList = ref([])
// 当前页码
const currentPage = ref(1)
// 每页显示条数
const pageSize = ref(10)
// 总记录数
const total = ref(0)
// 总页数（计算属性）
const totalPages = computed(() => {
  // 确保total和pageSize都是数字
  const totalNum = Number(total.value)
  const pageSizeNum = Number(pageSize.value)
  const pages = Math.ceil(totalNum / pageSizeNum)
  console.log('计算总页数:', pages, 'total:', totalNum, 'pageSize:', pageSizeNum)
  return pages
})
// 标签选择弹窗可见性
const labelDialogVisible = ref(false)
// 当前选中的文章
const currentArticle = ref(null)

// 搜索文献
const searchArticles = async () => {
  try {

    // 设置加载状态
    loading.value = true
    
    // 准备请求参数
    const keywords = searchForm.keywords.trim()
    if (!keywords) {
      ElMessage.warning('请输入关键词')
      loading.value = false
      return
    }
    
    // 构建请求体
    const requestBody = {
      exp: keywords.split(',').map(k => k.trim()).filter(k => k),
      date: searchForm.year ? Number(searchForm.year) : '',
      page: currentPage.value
    }
    
    // 调用接口
    const response = await api.post('/get_from_oilink/get_article_from_wanfang', requestBody)
    
    // 添加调试日志
    console.log('API响应:', response)
    console.log('响应数据:', response.data)
    console.log('total_count值:', response.data?.total_count)
    
    if (response.data && response.data.code === 200 && response.data.msg === 'success') {
      console.log('数据列表:', response.data.data)
      articleList.value = response.data.data || []
      // 设置总记录数，确保转换为数字类型
      const totalCount = response.data.total_count
      console.log('原始total_count类型:', typeof totalCount, '值:', totalCount)
      total.value = totalCount ? Number(totalCount) : 0
      console.log('转换后total值:', total.value, '类型:', typeof total.value)
    } else {
      ElMessage.error('搜索失败，可能未找到符合要求的内容：' + (response.data?.msg || '未知错误'))
      articleList.value = []
      total.value = 0
      console.log('错误情况，设置total为0')
    }
  } catch (error) {
    console.error('搜索文献失败，可能未找到符合要求的内容:', error)
    ElMessage.error('搜索失败，请稍后重试')
    articleList.value = []
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  searchForm.keywords = ''
  searchForm.year = ''
  currentPage.value = 1
  articleList.value = []
  total.value = 0
}



// 处理每页条数变化
const handleSizeChange = (size) => {
  console.log('切换每页条数:', size)
  pageSize.value = size
  currentPage.value = 1 // 重置到第一页
  searchArticles()
}

// 处理页码变化
const handleCurrentChange = (current) => {
  console.log('切换页码:', current)
  currentPage.value = current
  searchArticles()
}

// 截断文本函数
const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 处理添加到知识库
const handleAddToKnowledgeBase = (article) => {
  // 保存当前选中的文章
  currentArticle.value = article
  // 显示标签选择弹窗
  labelDialogVisible.value = true
}

// 处理标签选择
const handleLabelSelect = (data) => {
  const { label_id } = data
  
  if (currentArticle.value && label_id) {
    // 调用收藏接口（暂时预留）
    saveToKnowledgeBase(currentArticle.value, label_id)
  }
}

// 保存到知识库
const saveToKnowledgeBase = async (article, labelId) => {
  try {
    loading.value = true
    
    // 构建保存到知识库的请求参数
    const requestBody = {
      data_dict: {
        title: article.标题,
        abstract: article.摘要,
        keywords: article.关键词,
        doi: article.DOI,
        publish_time: article.发表时间 // 添加发表时间
      }, 
      type_id: 1, // 1表示文献类型
      label_id: labelId,
    }
    
    console.log('保存到知识库请求参数:', requestBody)
    
    // 调用真实的API接口
    const response = await api.post('/add_to_knowledge/add_knowledge', requestBody)
    
    if (response.data && response.data.code === 200 && response.data.msg === 'success') {
      ElMessage.success('已成功添加到知识库')
      // 更新当前文章的收藏状态
      if (currentArticle.value) {
        currentArticle.value.is_collected = 1
      }
    } else {
      ElMessage.error('添加到知识库失败：' + (response.data?.msg || '未知错误'))
    }
  } catch (error) {
    console.error('添加到知识库失败:', error)
    ElMessage.error('添加到知识库失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 可以在这里进行初始化操作
})
</script>

<style scoped>
.article-wanfang-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  min-height: 100vh;
}

.search-section {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.search-form {
  display: flex;
  align-items: center;
}

.results-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.results-stats {
  margin-bottom: 15px;
  font-size: 14px;
  color: #606266;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  background: #fafafa;
  border-radius: 8px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.title-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.title-popover {
  white-space: pre-wrap;
  word-break: break-word;
  padding: 10px;
}

.abstract-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.abstract-popover {
  white-space: pre-wrap;
  word-break: break-word;
  padding: 10px;
  line-height: 1.6;
}
</style>