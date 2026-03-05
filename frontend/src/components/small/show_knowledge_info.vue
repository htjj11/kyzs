<template>
  <div class="knowledge-info-container">
    <div class="knowledge-header">
      <h3 class="knowledge-title">{{ knowledgeData.title || '无标题' }}</h3>
      <div class="knowledge-meta">
        <span class="meta-item">ID: {{ knowledgeData.id }}</span>
        <span class="meta-item">标签ID: {{ knowledgeData.label_id }}</span>
        <span class="meta-item">类型ID: {{ knowledgeData.type_id }}</span>
        <span class="meta-item">用户ID: {{ knowledgeData.user_id }}</span>
      </div>
    </div>
    
    <div class="knowledge-content">
      <div class="content-section">
        <h4 class="section-title">内容</h4>
        <div class="content-body">
          <pre>{{ knowledgeData.content || '无内容' }}</pre>
        </div>
      </div>
      
      <div class="mark-section">
        <div class="mark-item">
          <strong>标记信息：</strong>
          <span>{{ knowledgeData.mark_info || '无标记信息' }}</span>
        </div>
      </div>
    </div>
    
    <div class="knowledge-actions" v-if="showActions">
      <button @click="onEdit" class="btn edit-btn" v-if="onEdit">编辑</button>
      <button @click="onDelete" class="btn delete-btn" v-if="onDelete">删除</button>
      <!-- 添加到大模型知识库按钮 -->
      <button 
        @click="onAddToKnowledgeBase"
        :disabled="knowledgeData.in_anything === 1 || isAdding"
        :class="['btn', knowledgeData.in_anything === 1 ? 'added-btn' : 'add-btn']"
        title="{{ knowledgeData.in_anything === 1 ? '请到大模型知识库管理界面删除' : '添加到大模型知识库' }}"
      >
        {{ isAdding ? '添加中...' : (knowledgeData.in_anything === 1 ? '已添加到大模型知识库' : '添加到大模型知识库') }}
      </button>
      <button @click="onClose" class="btn close-btn" v-if="onClose">关闭</button>
    </div>
    
    <!-- 文件夹选择对话框组件 -->
    <GetFolder 
      v-model:visible="showFolderDialog"
      @confirm="handleFolderSelected"
    />
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api/request'
import GetFolder from './get_folder.vue'

// 定义组件属性
const props = defineProps({
  // 知识库数据对象
  knowledgeData: {
    type: Object,
    default: () => ({
      id: '',
      title: '',
      content: '',
      label_id: '',
      user_id: '',
      type_id: '',
      mark_info: '',
      in_anything: 0 // 默认值设为0
    })
  },
  // 是否显示操作按钮
  showActions: {
    type: Boolean,
    default: false
  }
})

// 定义组件事件
const emit = defineEmits(['edit', 'delete', 'close', 'addToKnowledgeBase', 'updateStatus'])

// 添加加载状态
const isAdding = ref(false)
// 控制文件夹选择对话框的显示
const showFolderDialog = ref(false)

// 编辑操作
const onEdit = () => {
  emit('edit', props.knowledgeData)
}

// 删除操作
const onDelete = () => {
  emit('delete', props.knowledgeData.id)
}

// 关闭操作
const onClose = () => {
  emit('close')
}

// 添加到大模型知识库操作
const onAddToKnowledgeBase = () => {
  if (props.knowledgeData.in_anything === 1 || isAdding.value) {
    return
  }
  
  // 显示文件夹选择对话框
  showFolderDialog.value = true
}

// 处理文件夹选择结果
const handleFolderSelected = async (folderData) => {
  if (!folderData || !folderData.id) {
    return
  }
  
  try {
    isAdding.value = true
    
    // 调用接口，传递知识ID和选择的文件夹ID
    const response = await api.post('/llm/add_knowledge_to_anythingllm', {
      knowledge_id: props.knowledgeData.id,
      folder_id: folderData.id
    })
    
    // 检查响应
    if (response.data && response.data.code === 200 && response.data.msg === 'success') {
      ElMessage.success('添加到公共知识库成功')
      // 通知父组件更新状态
      emit('updateStatus', {
        id: props.knowledgeData.id,
        in_anything: 1
      })
      // 同时触发原有的添加事件
      emit('addToKnowledgeBase', props.knowledgeData)
    } else {
      ElMessage.error('添加失败：' + (response.data?.msg || '未知错误'))
    }
  } catch (error) {
    console.error('添加到大模型知识库失败:', error)
    ElMessage.error('添加失败，请稍后重试')
  } finally {
    isAdding.value = false
  }
}
</script>

<style scoped>
.knowledge-info-container {
  background: white;
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.knowledge-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.knowledge-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.knowledge-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.meta-item {
  font-size: 12px;
  color: #666;
  background: #f5f5f5;
  padding: 4px 10px;
  border-radius: 12px;
}

.knowledge-content {
  margin-bottom: 20px;
}

.content-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
}

.section-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 16px;
  background: #1890ff;
  margin-right: 8px;
  border-radius: 2px;
}

.content-body {
  background: #fafafa;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
}

.content-body pre {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.mark-section {
  background: #fff7e6;
  padding: 12px 16px;
  border-radius: 4px;
  border: 1px solid #ffe58f;
}

.mark-item {
  font-size: 14px;
  color: #d46b08;
  display: flex;
  align-items: flex-start;
}

.mark-item strong {
  margin-right: 8px;
  white-space: nowrap;
}

.knowledge-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 80px;
  text-align: center;
}

.edit-btn {
  background: #52c41a;
  color: white;
}

.edit-btn:hover {
  background: #73d13d;
}

.delete-btn {
  background: #ff4d4f;
  color: white;
}

.delete-btn:hover {
  background: #ff7875;
}

.add-btn {
  background: #1890ff;
  color: white;
}

.add-btn:hover {
  background: #40a9ff;
}

.added-btn {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.close-btn {
  background: #fff;
  border: 1px solid #d9d9d9;
  color: #666;
}

.close-btn:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .knowledge-info-container {
    padding: 16px;
    margin: 0;
    border-radius: 0;
    border: none;
  }
  
  .knowledge-title {
    font-size: 18px;
  }
  
  .knowledge-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .knowledge-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>