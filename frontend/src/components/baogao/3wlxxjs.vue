<template>
  <div class="wlxxjs-container">
    <h2 class="title">网络信息检索</h2>
    
    <div class="online-summary-container">
      <div class="input-section">
        <el-input
          v-model="queryText"
          placeholder="请输入需要总结的主题，例如：随钻地震、人工智能"
          style="width: 500px; margin-right: 10px;"
          clearable
          @keyup.enter="generateSummary"
        />
        <el-button type="primary" @click="generateSummary" :loading="loading">
          <i class="el-icon-refresh-left"></i> 生成总结
        </el-button>
      </div>
      
      <div class="result-section" v-if="resultData">
        <div class="result-title-container">
          <h2 class="result-title">{{ currentQuery }}</h2>
          <el-button 
            type="primary" 
            size="small" 
            @click="addToFavorites"
            :loading="loading"
          >
            添加收藏
          </el-button>
        </div>
        
        <div class="content-section">
          <div class="result-content" v-html="formattedContent"></div>
        </div>

        <!-- 参考来源信息 -->
        <div v-if="referenceData && referenceData.length > 0" class="references-section">
          <h3 class="references-title">参考来源</h3>
          <div v-for="(reference, index) in referenceData" :key="index" class="reference-item">
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
      
      <!-- 标签选择对话框 -->
      <getLabelList
        :visible="showLabelDialog"
        @update:visible="showLabelDialog = $event"
        @selectLabel="handleLabelSelected"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from "@/api/request.js";
import { ElMessage } from 'element-plus';
import { ElInput, ElButton } from 'element-plus';
import { getUserIdFromCookie } from '@/utils/authUtils.js';
import getLabelList from '@/components/small/get_label_list.vue';

// 响应式数据
const queryText = ref('');
const loading = ref(false);
const resultData = ref(null);
const referenceData = ref([]);
const currentQuery = ref('');
const showLabelDialog = ref(false);

// 格式化内容，处理文本格式
const formattedContent = computed(() => {
  if (!resultData.value) return '';
  
  let content = resultData.value;
  // 将换行符转换为HTML换行标签
  content = content.replace(/\n/g, '<br>');
  // 将Markdown标题转换为HTML标题
  content = content.replace(/^### (.+)$/gm, '<h3 class="answer-subtitle">$1</h3>');
  content = content.replace(/^## (.+)$/gm, '<h2 class="answer-subtitle">$1</h2>');
  content = content.replace(/^# (.+)$/gm, '<h1 class="answer-subtitle">$1</h1>');
  // 将列表项转换为HTML列表
  content = content.replace(/^- (.+)$/gm, '<ul><li>$1</li></ul>');
  // 合并连续的列表项
  content = content.replace(/<\/ul>\s*<ul>/g, '');
  
  // 处理引用标记 [^数字^]，将其转换为高亮的上标，并添加悬停提示
  content = content.replace(/\[\^(\d+)\^\]/g, (match, index) => {
    // 转换为数字索引，注意参考来源是从0开始的
    const refIndex = parseInt(index) - 1;
    if (refIndex >= 0 && refIndex < referenceData.value.length) {
      const reference = referenceData.value[refIndex];
      // 创建提示内容
      const tooltip = `${reference.title}\n${reference.url.replace(/`/g, '')}`;
      // 返回带有样式和提示的上标元素
      return `<sup class="reference-mark" title="${tooltip.replace(/"/g, '&quot;')}">[${index}]</sup>`;
    }
    // 如果找不到对应的参考来源，返回原始标记
    return match;
  });
  
  return content;
});

// 重置表单
const resetForm = () => {
  queryText.value = '';
  currentQuery.value = '';
  resultData.value = null;
  referenceData.value = [];
};

// 添加收藏
const addToFavorites = () => {
  if (!resultData.value) {
    ElMessage.warning('请先生成结果');
    return;
  }
  
  // 显示标签选择对话框
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
    
    // 准备收藏数据
    const data_dict = {
      date: currentDate,
      title: currentQuery.value,
      content: resultData.value,
      source: JSON.stringify(referenceData.value)
    };
    
    // 调用收藏接口
    const response = await axios.post('/add_to_knowledge/add_knowledge', {
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
    // 关闭对话框
    showLabelDialog.value = false;
  }
};

// 生成总结
const generateSummary = async () => {
  if (!queryText.value.trim()) {
    ElMessage.warning('请输入需要总结的主题');
    return;
  }

  loading.value = true;
  try {
    const response = await axios.post('/get_from_oilink/get_online_infomation_summary', {
      online_infomation: queryText.value.trim()
    });
    console.log('API响应数据:', response.data);

    if (response.data.code === 200 && response.data.data) {
      // 保存当前查询文本
      currentQuery.value = queryText.value.trim();
      
      // 从新的响应格式中提取正文内容
      const choices = response.data.data.choices;
      if (choices && choices.length > 0) {
        // 获取assistant的消息作为正文
        const assistantChoice = choices.find(choice => choice.message.role === 'assistant');
        if (assistantChoice) {
          resultData.value = assistantChoice.message.content;
        }
        
        // 获取tool的消息作为参考来源
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
.wlxxjs-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 20px;
}

title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.online-summary-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.input-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-section {
  background: #fff;
  padding: 24px;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}

.result-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  line-height: 1.5;
}

.meta-info {
  display: flex;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.meta-item {
  margin-right: 24px;
}

.content-section {
  margin-top: 20px;
}

.result-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.answer-subtitle {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-top: 20px;
  margin-bottom: 10px;
}

/* 引用标记样式 */
.reference-mark {
  color: #409eff;
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
  color: #1976d2;
  text-decoration: none;
}

/* 标题容器样式 */
.result-title-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.result-title-container .result-title {
  margin: 0;
  flex: 1;
}

.result-title-container .el-button {
  margin-left: 15px;
}

.references-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e6e6e6;
}

.references-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}

.reference-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.reference-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 10px;
}

.reference-url {
  font-size: 14px;
  margin-bottom: 10px;
}

.reference-url a {
  color: #409eff;
  text-decoration: none;
  word-break: break-all;
}

.reference-url a:hover {
  text-decoration: underline;
}

.reference-content {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  background: #fff;
  padding: 10px;
  border-radius: 3px;
  border: 1px solid #e6e6e6;
}
</style>