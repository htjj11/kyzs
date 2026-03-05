<template>
  <div class="ai-reference-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-loading-spinner /> 正在基于大模型+知识库生成内容,请稍后...
    </div>
    
    <!-- 内容区域 -->
    <div v-else class="ai-reference-content">
      <!-- 三步水平布局 -->
      <div class="three-steps-container">
        <!-- 第一步：选择知识库内容 -->
        <div class="step-container">
          <h3 class="step-title">第一步:选择知识库内容</h3>
          
          <!-- 筛选条件区域 -->
          <div class="filter-container">
            <div class="filter-row">
              <el-input 
                v-model="filterTitle" 
                placeholder="标题关键字" 
                clearable 
                style="width: 100%; margin-bottom: 8px;"
              />
              <el-input 
                v-model="filterContent" 
                placeholder="内容关键字" 
                clearable 
                style="width: 100%; margin-bottom: 8px;"
              />
              <el-select 
                v-model="filterLabelName" 
                placeholder="标签名称" 
                clearable 
                style="width: 100%; margin-bottom: 8px;"
              >
                <el-option 
                  v-for="label in uniqueLabels" 
                  :key="label" 
                  :label="label" 
                  :value="label"
                />
              </el-select>
              <el-select 
                v-model="filterTypeId" 
                placeholder="类型" 
                clearable 
                style="width: 100%; margin-bottom: 8px;"
              >
                <el-option 
                  v-for="option in typeOptions" 
                  :key="option.value" 
                  :label="option.label" 
                  :value="option.value"
                />
              </el-select>
              <el-button @click="applyFilter" style="width: 100%;">筛选</el-button>
            </div>
          </div>
          <!-- 知识库内容列表 -->
          <div class="knowledge-list-container">
            <el-checkbox-group v-model="selectedKnowledgeIds">
              <el-checkbox 
                v-for="knowledge in filteredKnowledgeList" 
                :key="knowledge.id" 
                :label="knowledge.id"
                style="display: block; margin-bottom: 12px;"
              >
                <div class="knowledge-item">
                  <div class="knowledge-title">{{ knowledge.title }}</div>
                  <div class="knowledge-meta">
                    <span>内容: {{ knowledge.content && knowledge.content.length > 30 ? knowledge.content.substring(0, 30) + '...' : knowledge.content }}</span>
                    <span>注释: {{ knowledge.mark_info}}</span>
                    <span>标签: {{ knowledge.label_name }}</span>
                  </div>
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </div>
          
          <!-- 已选择内容信息 -->
          <div class="selected-info">
            <h4>已选择 {{ selectedKnowledgeIds.length }} 项</h4>
            <div v-if="selectedKnowledgeIds.length > 0" class="selected-list">
              <div v-for="id in selectedKnowledgeIds" :key="id" class="selected-item">
                {{ getKnowledgeTitleById(id) }}
              </div>
            </div>
          </div>
        </div>

        <!-- 第二步：选择预设提示词 -->
        <div class="step-container">
          <h3 class="step-title">第二步:选择预设提示词</h3>
          <div class="prompt-filter-row">
            <el-input 
              v-model="filterPromptName" 
              placeholder="提示词名称关键字" 
              clearable 
              style="width: 100%; margin-bottom: 8px;"
            />
            <el-select 
              v-model="filterPromptType" 
              placeholder="提示词类型" 
              clearable 
              style="width: 100%; margin-bottom: 8px;"
            >
              <el-option 
                v-for="type in uniquePromptTypes" 
                :key="type" 
                :label="type" 
                :value="type"
              />
            </el-select>
            <el-button @click="applyPromptFilter" style="width: 100%;">筛选</el-button>
          </div>
          <div class="prompt-list-container">
            <el-checkbox-group v-model="selectedPromptIds">
              <el-checkbox 
                v-for="promptItem in filteredPromptList" 
                :key="promptItem.id" 
                :label="promptItem.id" 
                style="display: block; margin-bottom: 8px;"
              >
                <div class="prompt-item">
                  <div class="prompt-name">{{ promptItem.name }}</div>
                  <div class="prompt-type">类型: {{ promptItem.type }}</div>
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </div>

        <!-- 第三步：输入需求 -->
        <div class="step-container">
          <h3 class="step-title">第三步:输入需求</h3>
          <div class="demand-container">
            <el-input 
              v-model="inputDemand" 
              placeholder="请输入需求" 
              clearable 
              type="textarea"
              :rows="6"
              style="width: 100%; height: 100%;"
            />
          </div>
        </div>
      </div>



      <!-- 操作按钮 -->
      <div class="ai-reference-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit">提交</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/api/request';
import { getUserIdFromCookie } from '@/utils/authUtils';

// 定义props
const props = defineProps({
  recordId: {
    type: [Number, String],
    required: false
  },
  selectedText: {
    type: String,
    required: false,
    default: ''
  }
});

// 定义emits
const emit = defineEmits(['insert-success', 'close', 'insert-reference']);

// 状态定义
const loading = ref(false);
const knowledgeList = ref([]); // 原始知识库列表
const filteredKnowledgeList = ref([]); // 筛选后的知识库列表
const selectedKnowledgeIds = ref([]); // 选中的知识库ID列表
const filterTitle = ref(''); // 标题筛选
const filterContent = ref(''); // 内容筛选
const filterLabelName = ref(''); // 标签名称筛选
const filterTypeId = ref(''); // 类型ID筛选
const promptList = ref([]); // 提示词列表
const filteredPromptList = ref([]); // 筛选后的提示词列表
const selectedPromptIds = ref([]); // 选中的提示词ID
const inputDemand = ref(''); // 用户输入的需求

// 筛选条件


 
const filterPromptName = ref(''); // 提示词名称筛选
const filterPromptType = ref(''); // 提示词类型筛选

// 类型映射常量
const typeOptions = [
  { value: 1, label: '文献' },
  { value: 2, label: '专利' },
  { value: 3, label: '网络信息收藏' },
  { value: 4, label: '用户自定义上传文本' },
  { value: 5, label: '用户自定义上传文档' }
];

// 初始化数据
onMounted(() => {
  fetchKnowledgeList();
  fetchPromptList();
});

// 计算属性：获取唯一的提示词类型列表
const uniquePromptTypes = computed(() => {
  const types = new Set();
  promptList.value.forEach(item => {
    if (item.type && String(item.type).trim()) {
      types.add(String(item.type));
    }
  });
  return Array.from(types).sort();
});

// 计算属性：获取唯一的标签名称列表
const uniqueLabels = computed(() => {
  const labels = new Set();
  knowledgeList.value.forEach(item => {
    if (item.label_name !== undefined && item.label_name !== null && String(item.label_name).trim()) {
      labels.add(String(item.label_name));
    }
  });
  return Array.from(labels).sort();
});

// 计算属性：获取唯一的类型ID列表
const uniqueTypes = computed(() => {
  const types = new Set();
  knowledgeList.value.forEach(item => {
    if (item.type_id !== undefined && item.type_id !== null && String(item.type_id).trim()) {
      types.add(String(item.type_id));
    }
  });
  return Array.from(types).sort();
});

 

// 获取提示词列表
const fetchPromptList = async () => {
  try {
    const userId = getUserIdFromCookie();
    const response = await request.post('/get_setting/get_all_prompt', {
      user_id: userId
    });
    
    if (response && response.data && response.data.code === 200) {
      promptList.value = response.data.data || [];
      filteredPromptList.value = [...promptList.value]; // 初始时显示所有提示词
    } else {
      throw new Error(response?.data?.msg || '获取提示词列表失败');
    }
  } catch (error) {
    ElMessage.error('获取提示词列表失败: ' + (error.message || '未知错误'));
    console.error('Error fetching prompt list:', error);
  }
};

// 应用提示词筛选
const applyPromptFilter = () => {
  filteredPromptList.value = promptList.value.filter(item => {
    // 提示词名称筛选
    const nameMatch = !filterPromptName.value || 
      (item.name && item.name.toLowerCase().includes(filterPromptName.value.toLowerCase()));
    
    // 提示词类型筛选
    const typeMatch = !filterPromptType.value || 
      (item.type && String(item.type) === String(filterPromptType.value));
    
    return nameMatch && typeMatch;
  });
};

// 获取知识库内容列表
const fetchKnowledgeList = async () => {
  try {
    loading.value = true;
    const userId = getUserIdFromCookie();
    const response = await request.post('/get_knowledge/get_all_knowledge', {
      user_id: userId
    });
    
    if (response && response.data && response.data.code === 200) {
      knowledgeList.value = response.data.data || [];
      filteredKnowledgeList.value = [...knowledgeList.value]; // 初始时显示所有内容
    } else {
      throw new Error(response?.data?.msg || '获取知识库内容失败');
    }
  } catch (error) {
    ElMessage.error('获取知识库内容失败: ' + (error.message || '未知错误'));
    console.error('Error fetching knowledge list:', error);
  } finally {
    loading.value = false;
  }
};

// 应用筛选条件
const applyFilter = () => {
  filteredKnowledgeList.value = knowledgeList.value.filter(item => {
    // 标题筛选
    const titleMatch = !filterTitle.value || 
      (item.title && item.title.toLowerCase().includes(filterTitle.value.toLowerCase()));
    
    // 内容筛选
    const contentMatch = !filterContent.value || 
      (item.content && item.content.toLowerCase().includes(filterContent.value.toLowerCase()));
    
    // 标签名称筛选
    const labelMatch = !filterLabelName.value || 
      (item.label_name !== undefined && item.label_name === filterLabelName.value);
    
    // 类型ID筛选
    const typeMatch = !filterTypeId.value || 
      (item.type_id !== undefined && String(item.type_id) === String(filterTypeId.value));
    
    return titleMatch && contentMatch && labelMatch && typeMatch;
  });
};

// 根据ID获取知识库标题
const getKnowledgeTitleById = (id) => {
  const item = knowledgeList.value.find(item => item.id === id);
  return item ? item.title : `未知项 (ID: ${id})`;
};





 
// 处理提交
const handleSubmit = async () => {
  // 原代码：移除知识库内容选择的强制限制，允许不选择任何内容
  // if (selectedKnowledgeIds.value.length === 0) {
  //   ElMessage.warning('请至少选择一项知识库内容');
  //   return;
  // }
  
  try {
    // 显示加载状态
    loading.value = true;
    
    // 记录提交的信息
    console.log('提交已选择的知识库ID列表:', selectedKnowledgeIds.value);
    console.log('提交已选择的提示词ID列表:', selectedPromptIds.value);
    console.log('提交用户输入的需求:', inputDemand.value);

    // 调用AI生成摘要接口
    const response = await request.post('/get_review/get_summary_by_ai', {
      knowledge_ids: selectedKnowledgeIds.value,
      prompt_ids: selectedPromptIds.value,
      user_need: inputDemand.value
    });
    
    if (response && response.data && response.data.code === 200) {
      // 获取AI生成的摘要结果
      const aiSummary = response.data.data || '';
      console.log('AI生成的摘要结果:', aiSummary);
      
      // 返回结果给父组件
      emit('insert-success', {
        knowledgeIds: selectedKnowledgeIds.value,
        promptIds: selectedPromptIds.value,
        demand: inputDemand.value,
        summary: aiSummary
      });
      
      // 触发更新父组件的replacedText变量
      emit('insert-reference', aiSummary);
      
      ElMessage.success('提交成功，AI摘要已生成并替换选中文本');
      handleCancel();
    } else {
      throw new Error(response?.data?.msg || '调用AI生成摘要失败');
    }
  } catch (error) {
    ElMessage.error('提交失败: ' + (error.message || '未知错误'));
    console.error('Error submitting knowledge selection:', error);
  } finally {
    // 隐藏加载状态
    loading.value = false;
  }
};

// 处理取消
const handleCancel = () => {
  emit('close');
};
</script>

<style scoped>
.ai-reference-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-container {
  margin-bottom: 16px;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.filter-row {
  display: flex;
  align-items: center;
}



.prompt-filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 16px;
  color: #606266;
}

.ai-reference-content {
  display: flex;
  flex-direction: column;
  height: 100%; /* 继承父组件的100%高度 */
  padding: 20px;
  overflow-y: auto; /* 保持滚动条 */
}

/* 三步水平布局容器 */
.three-steps-container {
  display: flex;
  gap: 20px;
  height: calc(100% - 40px); /* 减去上下padding的高度 */
  flex: 1;
}

/* 单个步骤容器 */
.step-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  min-width: 0; /* 防止flex子项溢出 */
}

.step-title {
  margin: 0;
  padding: 16px 20px;
  background-color: #f5f7fa;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

/* 筛选容器优化 */
.filter-container {
  padding: 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.filter-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prompt-filter-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

/* 提示词列表容器 */
.prompt-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* 需求输入容器 */
.demand-container {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

/* 提示词项样式 */
.prompt-item {
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.prompt-item:hover {
  background-color: #f5f7fa;
}

.prompt-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  font-size: 14px;
}

.prompt-type {
  font-size: 12px;
  color: #909399;
}

/* 知识库列表容器优化 */
.knowledge-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}

.knowledge-item {
  padding: 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.knowledge-item:hover {
  background-color: #f5f7fa;
}

.knowledge-title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  font-size: 14px;
}

.knowledge-meta {
  display: flex;
  flex-wrap: wrap; /* 允许换行 */
  gap: 8px 16px; /* 垂直和水平间距 */
  font-size: 12px;
  color: #909399;
  word-break: break-word; /* 防止长文本溢出 */
}

.selected-info {
  background-color: #f0f2f5;
  padding: 12px 16px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.selected-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.selected-list {
  max-height: 100px;
  overflow-y: auto;
}

.selected-item {
  padding: 4px 0;
  font-size: 12px;
  color: #606266;
}

.ai-reference-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0;
  border-top: 1px solid #e4e7ed;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .three-steps-container {
    gap: 16px;
  }
}

@media (max-width: 992px) {
  .three-steps-container {
    flex-direction: column;
    height: auto;
  }
  
  .step-container {
    min-height: 400px;
  }
}
</style>