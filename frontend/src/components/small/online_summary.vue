<template>
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
    <!-- {{ resultData }}
    {{ referenceData }} -->
    <div class="result-section" v-if="resultData">
      <h2 class="result-title">{{ resultData.title }}</h2>
      
      <div class="meta-info">
        <span class="meta-item">来源：{{ resultData.source }}</span>
        <span class="meta-item">日期：{{ resultData.date }}</span>
        <span class="meta-item">作者：{{ resultData.author }}</span>
      </div>

      <div class="content-section">
        <div
          v-html="formattedContent"
          class="result-content"
          @mouseover="handleMouseOver"
          @mouseleave="handleMouseLeave"
        ></div>
      </div>

      <!-- 全部参考来源列表 -->
      <div v-if="referenceData?.length > 0" class="references-section">
        <h3 class="references-title">参考来源</h3>
        <ul class="references-list">
          <li v-for="ref in referenceData" :key="ref.index" class="reference-item">
            <span class="reference-index">[{{ ref.index }}]</span>
            <span class="reference-title">{{ ref.title }}</span>
            <a :href="ref.url.replace(/`/g, '')" class="reference-link" target="_blank" rel="noopener noreferrer">
              {{ ref.url.replace(/`/g, '').length > 80 ? ref.url.replace(/`/g, '').substring(0, 80) + '...' : ref.url.replace(/`/g, '') }}
            </a>
          </li>
        </ul>
      </div>

    </div>

    <!-- 引用提示框 -->
    <div
      v-if="tooltipVisible"
      class="reference-tooltip"
      :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
    >
      <div class="tooltip-title">{{ tooltipData.title }}</div>
      <div class="tooltip-url">{{ tooltipData.url }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from "@/api/request.js";
import { ElMessage } from 'element-plus';

// 组件名称
defineOptions({ name: 'OnlineSummary' });

// 响应式数据
const queryText = ref('');
const loading = ref(false);
const resultData = ref(null);
const referenceData = ref([]);
const tooltipVisible = ref(false);
const tooltipData = ref({});
const tooltipX = ref(0);
const tooltipY = ref(0);

// 格式化内容，将引用标记转换为可交互的元素
const formattedContent = computed(() => {
  if (!resultData.value?.content) return '';
  
  let content = resultData.value.content;
  // 查找所有引用标记 [^数字^] 并替换为带有data属性的上标span标签
  content = content.replace(/\[\^(\d+)\^\]/g, (match, index) => {
    return `<span class="reference-mark" data-index="${index}">${index}</span>`;
  });
  
  return content;
});

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
    console.log(response.data);

    if (response.data.code === 200) {
      resultData.value = response.data.data.response_content;
      referenceData.value = response.data.data.response_reference;
      console.log(referenceData.value,referenceData.value);
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

// 处理鼠标悬停事件，显示引用提示
const handleMouseOver = (event) => {
  const target = event.target;
  if (target.classList.contains('reference-mark')) {
    try {
      const index = target.getAttribute('data-index');
      // 确保referenceData是数组且不为空
      if (Array.isArray(referenceData.value) && referenceData.value.length > 0) {
        const reference = referenceData.value.find(ref => ref && ref.index !== undefined && ref.index.toString() === index);
        
        if (reference && reference.title && reference.url) {
          tooltipData.value = {
            title: reference.title,
            url: reference.url.replace(/`/g, '') // 移除URL中的反引号
          };
          
          // 设置提示框位置
          tooltipX.value = event.pageX + 10;
          tooltipY.value = event.pageY + 10;
          tooltipVisible.value = true;
        }
      }
    } catch (error) {
      console.error('处理引用提示时出错:', error);
      // 出错时隐藏提示框，防止显示错误内容
      tooltipVisible.value = false;
    }
  }
};

// 处理鼠标离开事件，隐藏引用提示
const handleMouseLeave = (event) => {
  if (event.target.classList.contains('reference-mark')) {
    tooltipVisible.value = false;
  }
};
</script>

<style scoped>
.online-summary-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.input-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.result-section {
  background: #fff;
  padding: 24px;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
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

.reference-mark {
      color: #409eff;
      cursor: pointer;
      position: relative;
      display: inline-block;
      padding: 0 2px;
      border-bottom: 1px dashed #409eff;
      vertical-align: super;
      font-size: 0.75em;
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

    .references-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .reference-item {
      padding: 10px 0;
      border-bottom: 1px dotted #e6e6e6;
      display: flex;
      align-items: flex-start;
      font-size: 14px;
      line-height: 1.5;
    }

    .reference-index {
      color: #409eff;
      font-weight: 600;
      margin-right: 8px;
      min-width: 20px;
    }

    .reference-title {
      flex: 1;
      color: #333;
      margin-right: 8px;
    }

    .reference-link {
      color: #909399;
      text-decoration: none;
      word-break: break-all;
      max-width: 300px;
    }

    .reference-link:hover {
      color: #409eff;
      text-decoration: underline;
    }

.reference-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-width: 300px;
  z-index: 2000;
  pointer-events: none;
}

.tooltip-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.tooltip-url {
  font-size: 11px;
  color: #ccc;
  word-break: break-all;
}
</style>