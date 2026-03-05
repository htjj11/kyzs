<template>
  <div class="article-juhe-container">
    <h3 class="page-title">文章检索（重庆聚合接口）</h3>
    
    <!-- 搜索表单 -->
    <div class="search-form">
      <div class="form-row">
        <div class="form-item">
          <label>关键词：</label>
          <el-input 
            v-model="searchParams.keywords" 
            placeholder="请输入关键词，多个关键词用逗号分隔"
            style="width: 300px;"
          />
        </div>
        
        <div class="form-item">
          <label>年份：</label>
          <el-date-picker
            v-model="searchParams.year"
            type="year"
            placeholder="选择年份"
            style="width: 150px;"
          />
        </div>
        
        <div class="form-actions">
          <el-button type="primary" @click="searchArticles">搜索</el-button>
          <el-button 
            type="default" 
            @click="useTranslation = !useTranslation"
            :class="{ 'is-active': useTranslation }"
          >
            {{ useTranslation ? '取消中转英搜索' : '中转英搜索' }}
          </el-button>
          <el-button @click="resetSearch">重置</el-button>
        </div>
      </div>
    </div>
    
    <!-- 数据展示 -->
    <div class="data-section">
      <el-table
        v-loading="loading"
        :data="articleList"
        style="width: 100%"
        border
        stripe
      >
        <el-table-column prop="标题" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="关键词" label="关键词" min-width="150" :formatter="formatKeywords" show-overflow-tooltip />
        <el-table-column prop="年份" label="年份" width="80" />
        <el-table-column prop="摘要" label="摘要" min-width="300" show-overflow-tooltip />
        <el-table-column prop="DOI" label="DOI" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="downloadArticle(scope.row['下载链接'])"
              v-if="scope.row['下载链接']"
              style="margin-right: 5px"
            >
              下载
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleCollect(scope.row)"
            >
              收藏
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <div class="simple-pagination">
          <button 
            class="page-btn"
            :disabled="searchParams.page <= 1"
            @click="handlePrevPage"
          >
            上一页
          </button>
          <span class="page-info">第 {{ searchParams.page }} 页</span>
          <button 
            class="page-btn"
            @click="handleNextPage"
          >
            下一页
          </button>
        </div>
      </div>
      
      <!-- 提示信息 -->
      <div v-if="error" class="error-message">
        <el-alert :message="error" type="error" show-icon :closable="false" />
      </div>
      
      <div v-if="!loading && articleList.length === 0" class="empty-message">
        <el-alert message="暂无符合条件的数据" type="info" show-icon :closable="false" />
      </div>
    </div>
    
    <!-- 标签选择弹窗组件 -->
    <GetLabelList
      v-model:visible="showLabelSelect"
      @select-label="handleLabelSelect"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import request from '../../api/request.js'
import { ElMessage } from 'element-plus'
import GetLabelList from '../small/get_label_list.vue'

// 搜索参数
const searchParams = reactive({
  keywords: '',
  year: null,
  page: 1
});

// 数据状态
const articleList = ref([]);
const loading = ref(false);
const error = ref('');
const total = ref(0);
// 新增：控制是否使用中转英搜索
const useTranslation = ref(false);

// 新增：翻译关键词的方法
const translateKeywords = async (keywords) => {
  try {
    const response = await request.post('/get_from_oilink/translate_keyword', {
      keyword: keywords
    });
    
    if (response.data.code === 200) {
      // 确保返回的是字符串类型，使用正确的字段路径获取翻译结果
      const data = response.data.data;
      const translatedResult = data && data.translate_result ? data.translate_result : keywords;
      // 处理可能返回的对象，确保返回字符串
      return typeof translatedResult === 'string' ? translatedResult : String(translatedResult || keywords);
    } else {
      ElMessage.warning(`关键词翻译失败: ${response.data.msg || '未知错误'}`);
      // 翻译失败时返回原关键词
      return keywords;
    }
  } catch (error) {
    console.error('翻译请求失败:', error);
    ElMessage.warning('翻译服务暂时不可用');
    // 发生错误时返回原关键词
    return keywords;
  }
};

// 搜索文章
const searchArticles = async () => {
  // 重置页码为1
  loading.value = true;
  error.value = '';
  
  try {
    // 获取关键词
    let keywords = searchParams.keywords;
    
    // 如果使用翻译功能且有关键词，先翻译
    if (useTranslation.value && keywords) {
      // 分离多个关键词
      const keywordArray = keywords.split(',').map(key => key.trim());
      
      // 翻译每个关键词
      const translatedKeywords = [];
      for (const keyword of keywordArray) {
        if (keyword) {
          const translated = await translateKeywords(keyword);
          translatedKeywords.push(translated);
        }
      }
      
      // 合并翻译后的关键词
      keywords = translatedKeywords.join(',');
      console.log('翻译后的关键词:', keywords);
    }
    
    // 准备请求数据
    const requestData = {
      exp: keywords ? keywords.split(',').map(key => key.trim()) : [],
      date: searchParams.year ? String(searchParams.year).match(/\d{4}/)?.[0] || null : null,
      page: searchParams.page,
      size: 10 // 固定每页10条
    };
    
    const response = await request.post('/get_from_oilink/get_article_from_juhe', requestData);
    
    if (response.data.code === 200) {
      articleList.value = response.data.data || [];
      total.value = articleList.value.length; // 假设接口返回的是当前页的数据，实际项目中应该从接口获取总条数
      ElMessage.success('搜索成功');
    } else {
      throw new Error(response.data.msg || '搜索失败');
    }
  } catch (err) {
    error.value = err.message || '搜索过程中发生错误';
    ElMessage.error(error.value);
  } finally {
    loading.value = false;
  }
};

// 重置搜索
const resetSearch = () => {
  searchParams.keywords = '';
  searchParams.year = null;
  searchParams.page = 1;
  articleList.value = [];
  total.value = 0;
  error.value = '';
};

 
// 处理上一页
const handlePrevPage = () => {
  if (searchParams.page > 1) {
    searchParams.page--;
    searchArticles();
  }
};

// 处理下一页
const handleNextPage = () => {
  searchParams.page++;
  searchArticles();
};

// 格式化关键词显示
const formatKeywords = (row) => {
  try {
    if (typeof row.关键词 === 'string') {
      // 尝试解析字符串形式的数组
      const parsed = JSON.parse(row.关键词.replace(/'/g, '"'));
      return Array.isArray(parsed) ? parsed.join(', ') : row.关键词;
    }
    return row.关键词;
  } catch {
    return row.关键词;
  }
};

// 下载文章
const downloadArticle = (downloadLink) => {
  if (downloadLink) {
    // 清理下载链接中的特殊字符
    const cleanLink = downloadLink.replace(/`/g, '').trim();
    window.open(cleanLink, '_blank');
    ElMessage.info('正在打开下载链接...');
  } else {
    ElMessage.warning('该文章暂无下载链接');
  }
};

// 收藏相关状态
const showLabelSelect = ref(false)
const currentArticle = ref(null)

// 处理收藏
const handleCollect = (row) => {
  currentArticle.value = row
  showLabelSelect.value = true
}

// 处理标签选择
const handleLabelSelect = async (data) => {
  if (!currentArticle.value || !data.label_id) return
  
  try {
    // 准备请求数据
    const requestData = {
      data_dict: {
        abstract: currentArticle.value['摘要'] || '',
        keywords: currentArticle.value['关键词'] ? currentArticle.value['关键词'].split(',').map(key => key.trim()) : [],
        title: currentArticle.value['标题'] || ''
      },
      label_id: data.label_id,
      type_id: 1
    }
    
    const response = await request.post('/add_to_knowledge/add_knowledge', requestData)
    
    if (response.data.code === 200) {
      ElMessage.success('收藏成功')
    } else {
      throw new Error(response.data.msg || '收藏失败')
    }
  } catch (error) {
    ElMessage.error(error.message || '收藏过程中发生错误')
  } finally {
    // 重置状态
    currentArticle.value = null
  }
}
</script>

<style scoped>
.article-juhe-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}

.search-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.form-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-item label {
  font-weight: 500;
  color: #666;
  min-width: 60px;
}

.form-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.data-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.simple-pagination {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-btn {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  background-color: #fff;
  color: #606266;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.page-btn:hover:not(:disabled) {
  color: #409eff;
  border-color: #c6e2ff;
}

.page-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.page-info {
  font-size: 14px;
  color: #606266;
  min-width: 80px;
  text-align: center;
}

.error-message,
.empty-message {
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .form-item {
    width: 100%;
  }
  
  .form-actions {
    margin-left: 0;
    justify-content: flex-end;
  }
  
  .pagination-container {
    justify-content: center;
  }
}
/* 新增：中转英搜索按钮激活状态样式 */
.el-button.is-active {
  background-color: #67c23a;
  border-color: #67c23a;
  color: #fff;
}

.el-button.is-active:hover {
  background-color: #85ce61;
  border-color: #85ce61;
  color: #fff;
}
</style>