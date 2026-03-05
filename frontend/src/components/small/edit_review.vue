<template>
  <div class="detail-container">
    <div class="edit-layout">
      <!-- 左侧：报告正文（可滚动） -->
      <div class="content-section">
        <div class="detail-item">
          <span class="label">ID:</span>
          <span class="value">{{ currentRecord.id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">报告正文:</span>
          <div 
            class="review-body scrollable"
            @mouseup="onTextSelection"
            @touchend="onTextSelection"
          >
            {{ currentRecord.review_body || '无内容' }}
          </div>
        </div>
      </div>
      
      <!-- 右侧：编辑栏（固定） -->
      <div class="edit-section">
        <div class="edit-header">
          <h4>文本编辑</h4>
        </div>
        
        <div v-if="!showEditInput" class="edit-hint">
          <p>请在左侧文本中选择需要修改的内容</p>
        </div>
        
        <!-- 文本修改输入框 -->
        <div v-else class="edit-input-container">
          <div class="edit-info">
            <span class="edit-label">选中文本:</span>
            <div class="selected-text scrollable-text">{{ selectedText }}</div>
          </div>
          <el-input
            v-model="replacedText"
            type="textarea"
            :rows="8"
            placeholder="请输入修改后的文本"
            class="edit-textarea"
          />
          <div class="edit-actions">
            <el-button @click="cancelEdit">取消</el-button>
            <el-button type="info" @click="showAiWindows()">
              引用
            </el-button>
            <el-button type="primary" :loading="editLoading" @click="submitEdit">确定修改</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- AI引用弹窗 -->
  <ElDialog
    v-model="aiWindowsVisible"
    title="AI引用生成"
    width="90%"
    height="90%"
    fullscreen
    append-to-body
  >
    <EditReviewAI 
      :record-id="currentRecord.id"
      :selected-text="selectedText"
      @insert-success="handleAiInsertSuccess"
      @insert-reference="handleInsertReference"
      @close="aiWindowsVisible = false"
    />
  </ElDialog>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '@/api/request';

import { ElDialog } from 'element-plus';
import EditReviewAI from './edit_review_ai.vue';

// 定义props
const props = defineProps({
  record: {
    type: Object,
    required: true
  }
});

// 定义emits
const emit = defineEmits(['update:modelValue', 'close']);

// 当前记录
const currentRecord = ref({});

// 文本编辑相关状态
const showEditInput = ref(false);
const selectedText = ref('');
const replacedText = ref('');
const editLoading = ref(false);
const selectionStart = ref(0);
const selectionEnd = ref(0);

// 引用弹窗相关
const aiWindowsVisible = ref(false);

// 初始化当前记录
const initCurrentRecord = () => {
  if (props.record && props.record.id) {
    currentRecord.value = { ...props.record };
  }
};

// 处理AI插入成功
const handleAiInsertSuccess = (selectedKnowledgeIds) => {
  // 这里可以处理AI引用插入成功后的逻辑
  console.log('AI引用插入成功，选中的知识库ID列表:', selectedKnowledgeIds);
  ElMessage.success('AI引用插入成功');
  aiWindowsVisible.value = false;
  // 如果需要在插入成功后刷新当前记录，可以调用initCurrentRecord()
  // initCurrentRecord();
};

// 处理文本选择
const onTextSelection = () => {
  const selection = window.getSelection();
  const text = selection.toString().trim();
  
  if (text && text.length > 0) {
    selectedText.value = text;
    replacedText.value = text; // 默认填充为选中的文本
    showEditInput.value = true;
    
    // 获取选中文本在原始内容中的起始和结束位置
    const reviewBodyElement = document.querySelector('.review-body');
    if (reviewBodyElement && currentRecord.value.review_body) {
      try {
        // 获取选中文本在页面中的位置
        const range = selection.getRangeAt(0);
        const startContainer = range.startContainer;
        const endContainer = range.endContainer;
        
        // 查找包含选中文本的段落
        let parent = startContainer;
        while (parent && parent !== reviewBodyElement) {
          parent = parent.parentNode;
        }
        
        if (parent === reviewBodyElement) {
          // 计算在完整文本中的位置
          const fullText = currentRecord.value.review_body;
          // 由于可能存在格式差异，使用文本匹配来估算位置
          // 这里采用简单的方法，实际应用中可能需要更复杂的算法
          const textBeforeSelection = fullText.substring(0, fullText.indexOf(text));
          selectionStart.value = textBeforeSelection.length;
          selectionEnd.value = selectionStart.value + text.length;
        }
      } catch (error) {
        console.error('获取选择位置失败:', error);
        // 如果获取位置失败，使用文本匹配作为备选方案
        const fullText = currentRecord.value.review_body;
        const index = fullText.indexOf(text);
        if (index !== -1) {
          selectionStart.value = index;
          selectionEnd.value = index + text.length;
        }
      }
    }
    
    // 滚动到编辑区域
    setTimeout(() => {
      const editContainer = document.querySelector('.edit-input-container');
      if (editContainer) {
        editContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
  }
};

// 取消编辑
const cancelEdit = () => {
  showEditInput.value = false;
  selectedText.value = '';
  replacedText.value = '';
  selectionStart.value = 0;
  selectionEnd.value = 0;
};

// 显示AI引用弹窗
const showAiWindows = () => {
  console.log('显示AI引用弹窗');
  aiWindowsVisible.value = true;
};

// 处理插入引用结果，由ai子组件调用此方法，传入文本
const handleInsertReference = (referenceText) => {
  if (referenceText) {
    replacedText.value = referenceText;
  }
};

// 提交修改
const submitEdit = async () => {
  if (!selectedText.value || !replacedText.value) {
    ElMessage.warning('请选择并输入要修改的内容');
    return;
  }
  
  if (replacedText.value === selectedText.value) {
    ElMessage.warning('修改后的内容与原内容相同');
    return;
  }
  
  // 确保有有效的位置信息
  if (selectionStart.value === 0 && selectionEnd.value === 0) {
    // 如果没有有效的位置信息，使用文本匹配作为备选
    const fullText = currentRecord.value.review_body;
    const index = fullText.indexOf(selectedText.value);
    if (index !== -1) {
      selectionStart.value = index;
      selectionEnd.value = index + selectedText.value.length;
    } else {
      ElMessage.error('无法确定选中内容的位置，请重新选择');
      return;
    }
  }
  
  editLoading.value = true;
  try {
    const response = await request.post('/get_review/modify_review', {
      review_id: currentRecord.value.id,
      start_position: selectionStart.value,
      end_position: selectionEnd.value,
      replaced_text: replacedText.value
    });
    
    if (response.data && response.data.code === 200) {
      ElMessage.success('修改成功');
      
      // 更新当前记录的内容（基于位置替换）
      const fullText = currentRecord.value.review_body;
      currentRecord.value.review_body = 
        fullText.substring(0, selectionStart.value) + 
        replacedText.value + 
        fullText.substring(selectionEnd.value);
      
      // 通知父组件更新数据
      emit('update:modelValue', currentRecord.value);
      
      // 重置编辑状态
      cancelEdit();
    } else {
      ElMessage.error(response.data?.msg || '修改失败');
    }
  } catch (error) {
    console.error('提交修改失败:', error);
    ElMessage.error('修改失败，请重试');
  } finally {
    editLoading.value = false;
  }
};

// 关闭编辑窗口
const handleClose = () => {
  emit('close');
};



// 生命周期钩子
onMounted(() => {
  initCurrentRecord();
});
</script>

<style scoped>
.detail-container {
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 0px;
  overflow: hidden;
  box-sizing: border-box;
}

.edit-layout {
  display: flex;
 height: 70vh;
  width: 100%;
  gap: 16px;
  padding: 16px;
  box-sizing: border-box;
}

/* 左侧内容区域 */
.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 16px;
  min-width: 0;
  box-sizing: border-box;
  overflow: hidden;
}

.detail-item {
  margin-bottom: 16px;
}

.detail-item:last-child {
  margin-bottom: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.label {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
  display: block;
}

.value {
  color: #606266;
}

.review-body.scrollable {
  flex: 1;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
  padding: 12px;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: text;
  min-height: 150px;
  min-height: 300px;
  height: 100%;
  max-height: none;
}

.review-body.scrollable:hover {
  background-color: #f9f9f9;
  
}

/* 右侧编辑区域 */
.edit-section {
  width: 360px;
  max-width: 40%;
  display: flex;
  flex-direction: column;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 300px;
}

.edit-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
}

.edit-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.edit-hint {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  text-align: center;
  padding: 20px;
}

.edit-input-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow-y: auto;
}

.edit-info {
  margin-bottom: 16px;
}

.edit-label {
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
  color: #333;
}

.selected-text {
  background-color: #e3f2fd;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #bbdefb;
  margin-bottom: 4px;
  font-size: 14px;
  line-height: 1.5;
}

.scrollable-text {
  max-height: 100px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.edit-textarea {
  flex: 1;
  margin-bottom: 16px;
  min-height: 120px;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .edit-layout {
    flex-direction: column;
    padding: 8px;
  }
  
  .edit-section {
    width: 100%;
    max-width: 100%;
    margin-top: 16px;
  }
}

/* 针对上级对话框的适配 */
@media (max-height: 600px) {
  .edit-layout {
    padding: 8px;
  }
  
  .content-section {
    padding: 12px;
  }
  
  .review-body.scrollable {
    min-height: 100px;
    max-height: calc(100% - 80px);
  }
}

@media (max-width: 900px) {
  .edit-section {
    width: 320px;
    max-width: 50%;
  }
}
</style>
