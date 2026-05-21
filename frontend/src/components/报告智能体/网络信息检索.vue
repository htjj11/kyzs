<template>
  <div class="wlxxjs-container" :class="{ 'has-result': searched }">
    <!-- 加载遮罩 -->
    <transition name="fade">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span class="loading-text">{{ loadingText }}</span>
      </div>
    </transition>

    <!-- 搜索区域 -->
    <div class="search-area">


      <div class="provider-row">
        <span class="provider-label">搜索源</span>
        <el-radio-group v-model="searchProvider" size="default" class="provider-radios">
          <el-radio-button value="xunfei">讯飞星火</el-radio-button>
          <el-radio-button value="doubao">豆包（火山方舟）</el-radio-button>
          <el-radio-button value="metaso">秘塔 AI</el-radio-button>
        </el-radio-group>
      </div>
      <div class="search-bar">
        <el-input v-model="queryText" placeholder="请输入需要总结的主题，例如：随钻地震、人工智能" clearable class="google-input"
          @keyup.enter="generateSummary" />
        <el-button class="google-btn" @click="generateSummary" :loading="loading">
          检索互联网
        </el-button>
      </div>
    </div>

    <!-- 结果区域 -->
    <transition name="result-fade">
      <div v-if="searched && resultData" class="result-section">
        <div class="result-title-container">
          <h2 class="result-title">{{ currentQuery }}</h2>
          <el-button type="primary" size="small" @click="addToFavorites" :loading="loading">
            添加收藏
          </el-button>
        </div>

        <div class="split-view">
          <div class="content-left">
            <div class="result-content" v-html="formattedContent" @mouseover="handleMouseOver"
              @mouseout="handleMouseOut"></div>
          </div>
          <div class="references-right" v-if="referenceData && referenceData.length > 0">
            <h3 class="references-title">参考来源</h3>
            <div v-for="(reference, index) in referenceData" :key="index" class="reference-item"
              :class="{ 'highlight-flash': highlightedRefIndex === index }">
              <div class="reference-title">
                {{ index + 1 }}. {{ reference.title }}
              </div>
              <div class="reference-url">
                网址：<a :href="reference.url.replace(/`/g, '')" target="_blank" rel="noopener noreferrer">
                  {{ reference.url.replace(/`/g, '') }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 标签选择对话框 -->
    <getLabelList :visible="showLabelDialog" @update:visible="showLabelDialog = $event"
      @selectLabel="handleLabelSelected" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { marked } from 'marked';
import axios from "@/api/request.js";
import { ElMessage } from 'element-plus';
import getLabelList from '@/components/small/get_label_list.vue';

// 响应式数据
const queryText = ref('');
/** xunfei | doubao | metaso，与后端 /get_source/get_online_infomation_summary 的 provider 一致 */
const searchProvider = ref('xunfei');
const loading = ref(false);
const loadingText = ref('正在生成总结…');
const resultData = ref(null);
const referenceData = ref([]);
const currentQuery = ref('');
const showLabelDialog = ref(false);
const searched = ref(false);
const highlightedRefIndex = ref(null); // 当前悬浮高亮的参考索引

// 格式化内容，处理文本格式
const formattedContent = computed(() => {
  if (!resultData.value) return '';

  // 使用 marked 解析标准的 Markdown 内容（包括列表、加粗、标题等）
  let htmlStr = marked.parse(resultData.value);

  // 处理 [^1^] 形式的引用标识为气泡或上标链接
  htmlStr = htmlStr.replace(/\[\^(\d+)\^\]/g, (match, index) => {
    const refIndex = parseInt(index) - 1;
    if (refIndex >= 0 && refIndex < referenceData.value.length) {
      const reference = referenceData.value[refIndex];
      const tooltip = `${reference.title}\n${reference.url.replace(/`/g, '')}`;
      return `<sup class="reference-mark" data-ref-index="${refIndex}" title="${tooltip.replace(/"/g, '&quot;')}">[${index}]</sup>`;
    }
    return match;
  });

  return htmlStr;
});

// 鼠标悬停在角标上
const handleMouseOver = (e) => {
  const target = e.target.closest('.reference-mark');
  if (target) {
    const index = parseInt(target.getAttribute('data-ref-index'));
    highlightedRefIndex.value = index;

    // 自动滚动右侧面板使对应的参考项可见
    const rightPanel = document.querySelector('.references-right');
    if (rightPanel) {
      const refElement = rightPanel.children[index + 1]; // +1 是因为有 h3 标题
      if (refElement) {
        refElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }
};

// 鼠标移出角标
const handleMouseOut = (e) => {
  const target = e.target.closest('.reference-mark');
  if (target) {
    highlightedRefIndex.value = null;
  }
};

// 添加收藏
const addToFavorites = () => {
  if (!resultData.value) {
    ElMessage.warning('请先生成结果');
    return;
  }
  showLabelDialog.value = true;
};

// 处理标签选择
const handleLabelSelected = async (labelData) => {
  try {
    if (!labelData || !labelData.label_id) {
      ElMessage.warning('请选择一个标签');
      return;
    }

    const currentDate = new Date().toISOString().split('T')[0];

    const data_dict = {
      date: currentDate,
      title: currentQuery.value,
      content: resultData.value,
      source: JSON.stringify(referenceData.value)
    };

    const response = await axios.post('/personal_knowledgebase/add_knowledge', {
      label_id: labelData.label_id,
      data_dict: data_dict,
      type_id: 3,
    });

    if (response.data.code === 200) {
      ElMessage.success('收藏成功');
    } else {
      ElMessage.error(response.data.msg || '收藏失败');
    }
  } catch (error) {
    ElMessage.error('收藏出错，请稍后重试');
    console.error('收藏错误:', error);
  } finally {
    showLabelDialog.value = false;
  }
};

// 生成总结
const generateSummary = async () => {
  if (!queryText.value.trim()) {
    ElMessage.warning('请输入需要总结的主题');
    return;
  }

  loadingText.value = '正在生成总结…';
  loading.value = true;
  try {
    const response = await axios.post('/get_source/get_online_infomation_summary', {
      online_infomation: queryText.value.trim(),
      provider: searchProvider.value,
    });
    console.log('API响应数据:', response.data);

    if (response.data.code === 200 && response.data.data) {
      currentQuery.value = queryText.value.trim();
      searched.value = true;

      const choices = response.data.data.choices;
      if (choices && choices.length > 0) {
        const assistantChoice = choices.find(choice => choice.message.role === 'assistant');
        if (assistantChoice) {
          resultData.value = assistantChoice.message.content;
        }

        const toolChoice = choices.find(choice => choice.message.role === 'tool');
        if (toolChoice && toolChoice.message.tool_calls && toolChoice.message.tool_calls.length > 0) {
          const webSearchCall = toolChoice.message.tool_calls.find(call => call.type === 'web_search');
          if (webSearchCall && webSearchCall.web_search && webSearchCall.web_search.outputs) {
            referenceData.value = webSearchCall.web_search.outputs;
          }
        }
      }

      console.log('结果数据:', resultData.value);
      console.log('参考数据:', referenceData.value);
      ElMessage.success('总结生成成功');
    } else {
      ElMessage.error(response.data.msg || '总结生成失败');
    }
  } catch (error) {
    ElMessage.error('网络错误，请稍后重试');
    console.error('API请求错误:', error);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* ===== 基础容器 ===== */
.wlxxjs-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 24px;
  box-sizing: border-box;
  background: #f4f6f8;
  overflow: hidden;
  transition: justify-content 0.4s ease, padding 0.4s ease;
}

.wlxxjs-container.has-result {
  justify-content: flex-start;
  padding: 16px 20px;
}

/* ===== 搜索区域 ===== */
.search-area {
  width: 100%;
  max-width: 680px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: all 0.35s ease;
}

.has-result .search-area {
  align-items: flex-start;
  max-width: 100%;
  margin-bottom: 12px;
}

.provider-row {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.provider-label {
  font-size: 14px;
  color: #5c6b8a;
  flex-shrink: 0;
}

.provider-radios :deep(.el-radio-button__inner) {
  border-radius: 20px;
  padding: 8px 14px;
}

.has-result .provider-row {
  margin-bottom: 10px;
}

/* ===== Google 风格搜索栏 ===== */
.search-bar {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 12px;
}

.google-input {
  flex: 1;
}

.google-input :deep(.el-input__wrapper) {
  border-radius: 24px;
  padding: 8px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  border: 1px solid #dfe1e5;
  transition: box-shadow 0.25s ease, border-color 0.25s ease;
}

.google-input :deep(.el-input__wrapper:hover),
.google-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.16);
  border-color: transparent;
}

.google-input :deep(.el-input__inner) {
  font-size: 16px;
  height: 28px;
  line-height: 28px;
}

.google-btn {
  flex-shrink: 0;
  border-radius: 24px;
  padding: 10px 28px;
  font-size: 15px;
  font-weight: 500;
  background: #1a5caa;
  color: #fff;
  border: none;
  cursor: pointer;
  transition: background 0.2s ease, box-shadow 0.2s ease;
}

.google-btn:hover {
  background: #164d8f;
  box-shadow: 0 2px 8px rgba(26, 92, 170, 0.35);
}

/* ===== 结果区域 ===== */
.result-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  padding: 20px 24px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  min-height: 0;
  width: 100%;
}

.result-title {
  font-size: 22px;
  font-weight: 600;
  color: #1a2b4a;
  margin-bottom: 12px;
  line-height: 1.4;
}

.result-title-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.result-title-container .result-title {
  margin: 0;
  flex: 1;
}

.result-title-container .el-button {
  margin-left: 15px;
}

/* ===== 左右分栏 ===== */
.split-view {
  display: flex;
  gap: 20px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.content-left {
  flex: 2;
  min-width: 0;
  overflow-y: auto;
}

.references-right {
  flex: 1;
  max-width: 350px;
  overflow-y: auto;
}

.result-content {
  font-size: 15px;
  line-height: 1.8;
  color: #333;
  word-wrap: break-word;
}

/* Markdown 生成的具体元素样式 */
.result-content :deep(h1),
.result-content :deep(h2),
.result-content :deep(h3),
.result-content :deep(h4) {
  font-weight: 600;
  color: #1a2b4a;
  margin-top: 18px;
  margin-bottom: 8px;
  line-height: 1.4;
}

.result-content :deep(h1) {
  font-size: 22px;
}

.result-content :deep(h2) {
  font-size: 20px;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 4px;
}

.result-content :deep(h3) {
  font-size: 18px;
}

.result-content :deep(p) {
  margin-bottom: 12px;
}

.result-content :deep(ul),
.result-content :deep(ol) {
  padding-left: 20px;
  margin-bottom: 12px;
}

.result-content :deep(li) {
  margin-bottom: 4px;
}

.result-content :deep(strong) {
  font-weight: 600;
  color: #111;
}

/* ===== 引用标记 ===== */
.reference-mark {
  color: #1a5caa;
  font-weight: bold;
  cursor: pointer;
  text-decoration: underline;
  margin: 0 2px;
  font-size: 0.75em;
  position: relative;
  top: -0.5em;
}

.reference-mark:hover {
  background-color: #e3f2fd;
  color: #1565c0;
  text-decoration: none;
}

/* ===== 参考来源 ===== */
.references-title {
  font-size: 17px;
  font-weight: 600;
  color: #1a2b4a;
  margin-bottom: 12px;
}

.reference-item {
  background: #f8f9fa;
  padding: 12px 14px;
  border-radius: 6px;
  border-left: 3px solid #1a5caa;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

/* 高亮闪烁动画 */
.reference-item.highlight-flash {
  animation: flashHighlight 1s ease infinite alternate;
  transform: translateX(-4px);
  border-left-width: 4px;
  box-shadow: 0 4px 12px rgba(26, 92, 170, 0.15);
}

@keyframes flashHighlight {
  0% {
    background-color: #e3f2fd;
    border-left-color: #1a5caa;
  }

  100% {
    background-color: #bbdefb;
    border-left-color: #0d47a1;
  }
}

.reference-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.reference-url {
  font-size: 13px;
  margin-bottom: 0;
}

.reference-url a {
  color: #1a5caa;
  text-decoration: none;
  word-break: break-all;
}

.reference-url a:hover {
  text-decoration: underline;
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