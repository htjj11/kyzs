<script setup>
import { ref, reactive } from 'vue';
import axios from "@/api/request.js";
import { ElTable, ElTableColumn, ElInput, ElButton, ElMessage, ElDialog, ElSelect, ElOption, ElCheckbox } from 'element-plus';
import { getUserIdFromCookie } from '@/utils/authUtils.js';



// 响应式数据
const keywords = ref('');
const page = ref(1);
const size = ref(10);
const total = ref(0);
const totalPages = ref(0);
const tableData = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
// 标签选择相关数据
const tagDialogVisible = ref(false);
const userTags = ref([]);
const selectedTag = ref('');
const currentRow = ref(null);
// 新增：控制是否使用中转英搜索
const useTranslation = ref(false);

// 新增：翻译关键词的方法
const translateKeywords = async (keywords) => {
  try {
    const response = await axios.post('/get_from_oilink/translate_keyword', {
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

// 搜索方法
const searchArticles = async () => {
  if (!keywords.value.trim()) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }

  loading.value = true;
  // 前端页码从1开始，API页码从0开始，需要转换
    const apiPage = page.value - 1;
    
    // 验证页码有效性
    if (apiPage < 0) {
      ElMessage.error('页码不能小于1');
      loading.value = false;
      return;
    }
    
    try {
      let searchKeywords = keywords.value;
      
      // 如果勾选了中转英搜索，先翻译关键词
      if (useTranslation.value) {
        // 分离多个关键词
        const keywordArray = searchKeywords.split(',').map(k => k.trim());
        
        // 翻译每个关键词
        const translatedKeywords = [];
        for (const keyword of keywordArray) {
          if (keyword.trim()) {
            const translated = await translateKeywords(keyword.trim());
            translatedKeywords.push(translated);
          }
        }
        
        // 合并翻译后的关键词
        searchKeywords = translatedKeywords.join(',');
        // 将翻译后的关键词更新到搜索框
        keywords.value = searchKeywords;
        console.log('翻译后的关键词:', searchKeywords);
      }
      
      const response = await axios.post('/get_from_oilink/get_articles', {
        keywords_list: searchKeywords.split(',').map(k => k.trim()),
        page: apiPage,
        size: size.value,
      });

    if (response.data.code === 200) {
        console.log('搜索接口返回：',response.data);
        tableData.value = response.data.data;
        total.value = response.data.total || 0; // 假设API返回total字段
        totalPages.value = Math.ceil(total.value / size.value) || 1;
      } else {
      ElMessage.error(response.data.msg || '获取数据失败');
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试');
    console.error('API请求错误:', error);
  } finally {
    loading.value = false;
  }
};

// 上一页
const prevPage = () => {
  if (page.value > 1) {
    page.value--;
    searchArticles();
  }
};

// 下一页
const nextPage = () => {
  if (1) {
    page.value++;
    searchArticles();
  }
};


// 显示标签选择对话框
const showTagDialog = async (row) => {
  currentRow.value = row;
  selectedTag.value = '';
  
  try {
    // 获取用户标签
    const response = await axios.post('/get_setting/get_all_label', {
      user_id: getUserIdFromCookie()// 这里假设用户ID为1，实际应该从登录信息中获取  
    });
    
    if (response.data.code === 200) {
      userTags.value = response.data.data || [];
      tagDialogVisible.value = true;
    } else {
      ElMessage.error(response.data.msg || '获取标签失败');
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试');
    console.error('获取标签失败:', error);
  }
};

// 确认添加收藏
const confirmCollect = () => {
  if (!selectedTag.value) {
    ElMessage.warning('请选择标签，若为第一次使用，请到设置中增加标签');
    return;
  }
  
  axios.post('/add_to_knowledge/add_knowledge', {
    data_dict: currentRow.value,
    type_id: 1,
    label_id: selectedTag.value
  }).then(res => {
    console.log('增加收藏接口返回：', res.data);
    if (res.data['code'] == 200) {
      ElMessage.success('收藏成功');
      currentRow.value.is_collected = 1;
      tagDialogVisible.value = false;
    } else {
      ElMessage.error(res.data.msg || '收藏失败');
    }
  }).catch(error => {
    ElMessage.error('网络错误，请稍后重试');
    console.error('API请求错误:', error);
  });
};

// 取消标签选择
const cancelTagSelection = () => {
  tagDialogVisible.value = false;
  selectedTag.value = '';
  currentRow.value = null;
};


</script>

<template>
  <div class="search-container">
    <h1>文献检索（oilink资源）</h1>
    <div class="search-form">
      <ElInput
        v-model="keywords"
        placeholder="请输入关键词，多个关键词用逗号分隔"
        style="width: 500px; margin-right: 10px;"
        clearable
      />
      <ElButton type="primary" @click="searchArticles">搜索</ElButton>
      <ElCheckbox v-model="useTranslation" style="margin-left: 10px;">中转英搜索</ElCheckbox>

      <!-- 标签选择对话框 -->
      <ElDialog
        title="选择标签"
        v-model="tagDialogVisible"
        width="400px"
        :close-on-click-modal="false"
      >
        <div style="margin-bottom: 20px;">
          <ElSelect
            v-model="selectedTag"
            placeholder="请选择标签"
            style="width: 100%;"
          >
            <ElOption
              v-for="tag in userTags"
              :key="tag.id"
              :label="tag.label_name"
              :value="tag.id"
            />
          </ElSelect>
        </div>
        <template #footer>
          <ElButton @click="cancelTagSelection">取消</ElButton>
          <ElButton type="primary" @click="confirmCollect">确认收藏</ElButton>
        </template>
      </ElDialog>
    </div>

    <div class="table-container">
      <ElTable
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
      >
        <ElTableColumn label="文献标题" width="300">
          <template #default="scope">
            <span>{{ scope.row.title_zh || scope.row.title || '无标题' }}</span>
          </template>
        </ElTableColumn>
        <ElTableColumn label="关键词">
          <template #default="scope">
            <span v-if="scope.row.keywords_zh">{{ scope.row.keywords_zh.join(', ') }}</span>
            /
            <span v-if="scope.row.keywords">{{ scope.row.keywords.join(', ') }}</span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="year" label="年份" width="80" />
        <ElTableColumn label="中文摘要">
          <template #default="scope">
            <div class="abstract-content">{{ scope.row.abstract_zh || scope.row.abstract || '无' }}</div>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="doi" label="DOI" width="180" />
        <ElTableColumn label="收藏" width="100">
          <template #default="scope">
             <div v-if="scope.row.is_collected === 1"> 
              已收藏至知识库
            </div>
            <ElButton
              v-if="scope.row.is_collected === 0"
              type="primary"
              size="small"
              @click="showTagDialog(scope.row, 1)"
            >
              添加收藏
            </ElButton>
          </template>
        </ElTableColumn>
      </ElTable>

      <div class="custom-pagination" style="margin-top: 16px; text-align: center;">
        <ElButton
          @click="prevPage"
          :disabled="page <= 1"
          icon="ArrowLeft"
          size="small"
        >
          上一页
        </ElButton>
        <span style="margin: 0 16px;">
          第 {{ page }} 页 / 共 {{ totalPages }} 页
        </span>
        <ElButton
          @click="nextPage"
           
          icon="ArrowRight"
          size="small"
        >
          下一页
        </ElButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  padding: 20px;
}

.search-form {
  margin: 20px 0;
  display: flex;
  align-items: center;
}

.table-container {
  margin-top: 20px;
}

.pagination-container {
  margin-top: 15px;
  text-align: right;
}

.abstract-content {
  max-width: 500px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.read-the-docs {
  color: #888;
}
</style>
