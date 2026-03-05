<template>
  <div class="knowledge-base-container">
    <!-- 筛选条件区域 -->
    <div class="filter-section">
      <!-- 标签筛选标签页 -->
      <div class="label-tabs-container">
        <div class="label-tabs">
          <button 
            class="label-tab" 
            :class="{ active: !filters.labelId }"
            @click="selectLabel('')"
          >
            全部标签
          </button>
          <button 
            v-for="label in labelList" 
            :key="label.id"
            class="label-tab"
            :class="{ active: filters.labelId === label.id.toString() }"
            @click="selectLabel(label.id.toString())"
          >
            {{ label.label_name }}
          </button>
        </div>
      </div>
      
      <!-- 其他筛选条件 -->
      <div class="filter-row">
        <div class="filter-item">
          <label>标题包含：</label>
          <input v-model="filters.title" type="text" placeholder="请输入标题关键字" class="filter-input">
        </div>
        
        <div class="filter-item">
          <label>内容包含：</label>
          <input v-model="filters.content" type="text" placeholder="请输入内容关键字" class="filter-input">
        </div>
        
        <div class="filter-item">
          <label>类型：</label>
          <el-select v-model="filters.typeId" placeholder="请选择类型" class="filter-input">
            <el-option label="全部类型" value=""></el-option>
            <el-option label="文献" value="1"></el-option>
            <el-option label="专利" value="2"></el-option>
            <el-option label="网络信息收藏" value="3"></el-option>
            <el-option label="用户自定义上传文本" value="4"></el-option>
            <el-option label="用户自定义上传文档" value="5"></el-option>
          </el-select>
        </div>
        
        <div class="filter-item">
          <label>标记信息：</label>
          <input v-model="filters.markInfo" type="text" placeholder="请输入标记信息关键字" class="filter-input">
        </div>
        
        <div class="filter-actions-inline">
          <button @click="resetFilters" class="btn reset-btn">重置筛选</button>
        </div>
      </div>
    </div>
    
    <!-- 数据展示区域 -->
    <div class="data-section">
      <div v-if="loading" class="loading-state">
        <span>加载中...</span>
      </div>
      
      <div v-else-if="error" class="error-state">
        <span>加载失败：{{ error }}</span>
        <button @click="fetchKnowledgeList" class="btn retry-btn">重试</button>
      </div>
      
      <div v-else>
        <div class="data-summary">
          <span>共 {{ filteredKnowledgeList.length }} 条记录（原始数据：{{ knowledgeList.length }} 条）</span>
        </div>
        
        <div class="knowledge-list">
          <div v-for="item in filteredKnowledgeList" :key="item.id" class="knowledge-item">
            <div class="item-header">
              <h3 class="item-title">{{ item.title }}</h3>
              <div class="item-meta">
                <span class="meta-label">ID: {{ item.id }}</span>
                <span class="meta-label">标签: {{ item.label_name }}</span>
                <span class="meta-label">类型: {{ getTypeName(item.type_id) }}</span>
              </div>
            </div>
            
            <div class="item-content">
              <p>{{ truncateText(item.content, 200) }}</p>
            </div>
            
            <div class="item-footer">
              <span class="mark-info">标记信息：{{ item.mark_info }}</span>
              <div class="item-actions">
                <button @click="editKnowledge(item)" class="action-btn edit-btn">编辑</button>
                <button @click="deleteKnowledge(item.id)" class="action-btn delete-btn">删除</button>
                <button @click="viewKnowledge(item)" class="action-btn view-btn">查看详情</button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="filteredKnowledgeList.length === 0" class="empty-state">
          <span>暂无符合条件的知识库记录</span>
        </div>
      </div>
    </div>
  </div>

  <!-- 知识库详情弹窗（全屏） -->
  <el-dialog
    v-model="showDetailModal"
    title="知识库详情"
    fullscreen
    :before-close="closeDetailModal"
    append-to-body
  >
    <template #default>
      <show-knowledge-info 
        v-if="selectedKnowledgeItem"
        :knowledgeData="selectedKnowledgeItem"
        :show-actions="true"
        @edit="handleDetailEdit"
        @delete="handleDetailDelete"
        @close="closeDetailModal"
      />
    </template>
  </el-dialog>

  <!-- 知识库编辑弹窗 -->
  <el-dialog
    v-model="showEditModal"
    title="编辑知识库"
    :width="'60%'"
    :before-close="closeEditModal"
    append-to-body
  >
    <template #default>
      <div class="edit-form">
        <div class="form-item">
          <label class="form-label">知识ID</label>
          <el-input v-model="editForm.knowledge_id" disabled placeholder="知识ID" />
        </div>
        
        <div class="form-item">
          <label class="form-label">知识名称 <span class="required">*</span></label>
          <el-input v-model="editForm.knowledge_title" placeholder="请输入知识名称" />
        </div>
        
        <div class="form-item">
          <label class="form-label">知识内容 <span class="required">*</span></label>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <el-input 
              v-model="editForm.knowledge_content" 
              type="textarea" 
              :rows="6" 
              placeholder="请输入知识内容"
            />
            <el-button 
              type="primary" 
              size="small"
              @click="openAiEditModal"
              style="align-self: flex-start;">
              AI修改
            </el-button>
          </div>
        </div>
        
        <div class="form-item">
          <label class="form-label">知识标签 <span class="required">*</span></label>
          <el-select v-model="editForm.knowledge_label" placeholder="请选择标签">
            <el-option 
              v-for="label in labelList" 
              :key="label.id" 
              :label="label.label_name" 
              :value="label.id"
            ></el-option>
          </el-select>
        </div>
        
        <div class="form-item">
          <label class="form-label">知识类型 <span class="required">*</span></label>
          <el-select v-model="editForm.knowledge_type" placeholder="请选择知识类型">
            <el-option label="文献" value="1"></el-option>
            <el-option label="专利" value="2"></el-option>
            <el-option label="网络信息收藏" value="3"></el-option>
            <el-option label="用户自定义上传文本" value="4"></el-option>
            <el-option label="用户自定义上传文档" value="5"></el-option>
          </el-select>
        </div>
        
        <div class="form-item">
          <label class="form-label">备注</label>
          <el-input v-model="editForm.knowledge_mark_info" placeholder="请输入备注信息" />
          <span style="font-size: 12px; color: #909399;">（如果数据来自于专利、文献，请勿手动修改）</span>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closeEditModal">取消</el-button>
        <el-button type="primary" @click="saveEdit">确定</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- AI修改弹窗 -->
  <el-dialog
    v-model="showAiEditModal"
    title="AI修改知识内容"
    :width="'60%'"
    :before-close="closeAiEditModal"
    append-to-body
  >
    <template #default>
      <div class="ai-edit-form">
        <div class="form-item">
          <label class="form-label">原文</label>
          <el-input 
            v-model="aiEditForm.originalContent" 
            type="textarea" 
            :rows="6" 
            disabled
            placeholder="知识内容原文"
          />
        </div>
        
        <div class="form-item">
          <label class="form-label">修改意见 <span class="required">*</span></label>
          <el-input 
            v-model="aiEditForm.prompt" 
            type="textarea" 
            :rows="4" 
            placeholder="请输入您的修改需求，例如：润色、缩短、扩写等"
          />
        </div>
        
        <!-- 提示词选择区域 -->
        <div class="form-item">
          <label class="form-label">预设提示词</label>
          
          <!-- 提示词筛选 -->
          <div class="prompt-filter-row">
            <el-input 
              v-model="filterPromptName" 
              placeholder="提示词名称关键字" 
              clearable 
              style="width: 200px; margin-right: 12px; margin-bottom: 8px;"
            />
            <el-button 
              type="primary" 
              size="small" 
              @click="applyPromptFilter"
              style="margin-bottom: 8px;"
            >
              筛选
            </el-button>
          </div>
          
          <!-- 提示词选择列表 -->
          <div v-if="promptLoading" class="prompt-loading">
            <span>加载提示词中...</span>
          </div>
          <div v-else-if="filteredPromptList.length > 0" class="prompt-list">
            <el-checkbox-group v-model="selectedPromptIds">
              <el-checkbox 
                v-for="promptItem in filteredPromptList" 
                :key="promptItem.id" 
                :label="promptItem.id" 
                style="margin-right: 16px; margin-bottom: 8px; display: inline-block;"
              >
                {{ promptItem.name }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
          <div v-else class="prompt-empty">
            <span>暂无提示词</span>
          </div>
        </div>
      </div>
    </template>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="closeAiEditModal">取消</el-button>
        <el-button type="primary" @click="submitAiEdit">确认修改</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import request from '@/api/request'
import { ElMessage, ElMessageBox, ElSelect, ElOption, ElLoading } from 'element-plus'
import ShowKnowledgeInfo from '@/components/small/show_knowledge_info.vue'

// 知识库列表数据
const knowledgeList = ref([])
const loading = ref(false)
const error = ref('')

// 标签列表数据
const labelList = ref([])

// 筛选条件
const filters = ref({
  title: '',
  content: '',
  labelId: '',
  typeId: '',
  markInfo: ''
})

// 从cookie中获取user_id
const getUserIdFromCookie = () => {
  const cookieValue = document.cookie
    .split('; ') 
    .find(row => row.startsWith('user_id=')) 
    ?.split('=')[1];
  // 如果cookie中没有user_id或值无效，返回默认值1
  return cookieValue && !isNaN(Number(cookieValue)) ? Number(cookieValue) : 1;
}

// 获取知识库列表
const fetchKnowledgeList = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 从cookie中获取user_id
    const userId = getUserIdFromCookie();
    const response = await request.post('/get_knowledge/get_all_knowledge', {
      user_id: userId
    })
    if (response.data['code'] === 200) {
        console.log('获取全部知识库内容：',response.data['data'])
      knowledgeList.value = response.data['data'] 
      ElMessage.success('数据加载成功')
    } else {
      throw new Error(response.msg || '获取数据失败')
    }
  } catch (err) {
    error.value = err.message
    ElMessage.error(`获取数据失败：${err.message}`)
  } finally {
    loading.value = false
  }
}

// 计算筛选后的知识库列表
const filteredKnowledgeList = computed(() => {
  return knowledgeList.value.filter(item => {
    // 标题筛选
    if (filters.value.title && !item.title.includes(filters.value.title)) {
      return false
    }
    
    // 内容筛选
    if (filters.value.content && !item.content.includes(filters.value.content)) {
      return false
    }
    
    // 标签ID筛选
    if (filters.value.labelId && item.label_id !== parseInt(filters.value.labelId)) {
      return false
    }
    
    // 类型ID筛选
    if (filters.value.typeId && item.type_id !== parseInt(filters.value.typeId)) {
      return false
    }
    
    // 标记信息筛选
    if (filters.value.markInfo && !item.mark_info.includes(filters.value.markInfo)) {
      return false
    }
    
    return true
  })
})

// 选择标签页
const selectLabel = (labelId) => {
  filters.value.labelId = labelId
  ElMessage.info(`已选择标签：${labelId ? labelList.value.find(l => l.id.toString() === labelId)?.label_name || '未知标签' : '全部标签'}`)
}

// 重置筛选条件，包括标签选择
const resetFilters = () => {
  filters.value = {
    title: '',
    content: '',
    labelId: '', // 重置标签选择为默认的"全部标签"
    typeId: '',
    markInfo: ''
  }
  ElMessage.info('筛选条件已重置')
}

// 截断文本显示
const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// 编辑弹窗相关变量
const showEditModal = ref(false)
const editForm = ref({
  knowledge_id: 0,
  knowledge_title: '',
  knowledge_content: '',
  knowledge_label: 0,
  knowledge_type: 0,
  knowledge_mark_info: ''
})

// 编辑知识库
const editKnowledge = (item) => {
  // 填充编辑表单数据
  editForm.value = {
    knowledge_id: item.id,
    knowledge_title: item.title,
    knowledge_content: item.content,
    knowledge_label: item.label_id,
    knowledge_type: item.type_id,
    knowledge_mark_info: item.mark_info
  }
  // 显示编辑弹窗
  showEditModal.value = true
}

// 保存编辑
const saveEdit = async () => {
  try {
    // 调用更新接口
    const response = await request.post('/get_knowledge/update_knoledge_by_id', {
      knowledge_id: editForm.value.knowledge_id,
      knowledge_title: editForm.value.knowledge_title,
      knowledge_content: editForm.value.knowledge_content,
      knowledge_label: editForm.value.knowledge_label,
      knowledge_type: editForm.value.knowledge_type,
      knowledge_mark_info: editForm.value.knowledge_mark_info
    })

    if (response.data['code'] === 200) {
      ElMessage.success('更新成功')
      // 关闭弹窗
      showEditModal.value = false
      // 重新获取知识库列表
      await fetchKnowledgeList()
    } else {
      throw new Error(response.msg || '更新失败')
    }
  } catch (err) {
    ElMessage.error(`更新失败：${err.message || '未知错误'}`)
  }
}

// 关闭编辑弹窗
const closeEditModal = () => {
  showEditModal.value = false
  // 重置表单
  editForm.value = {
    knowledge_id: 0,
    knowledge_title: '',
    knowledge_content: '',
    knowledge_label: 0,
    knowledge_type: 0,
    knowledge_mark_info: ''
  }
}

// 删除知识库
const deleteKnowledge = async (id) => {
  try {
    // 显示确认对话框
    const confirmResult = await ElMessageBox.confirm(
      '确定要删除这条知识库记录吗？删除后绑定的公共知识库也会删除。此操作不可撤销。',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }
    )

    if (confirmResult === 'confirm') {
      // 调用删除接口
      const response = await request.post('/get_knowledge/delete_knoledge_by_id', {
        knowledge_id: id
      })

      if (response.data['code'] === 200) {
        ElMessage.success('删除成功')
        // 重新获取知识库列表
        await fetchKnowledgeList()
      } else {
        throw new Error(response.msg || '删除失败')
      }
    }
  } catch (err) {
    // 如果用户取消，不显示错误信息
    if (err !== 'cancel') {
      ElMessage.error(`删除失败：${err.message || '未知错误'}`)
    }
  }
}

// 详情弹窗相关变量
const showDetailModal = ref(false)
const selectedKnowledgeItem = ref(null)

// 查看知识库详情
const viewKnowledge = (item) => {
  console.log('查看单条收藏详情：',item)
  selectedKnowledgeItem.value = item
  showDetailModal.value = true
}

// 关闭详情弹窗
const closeDetailModal = () => {
  showDetailModal.value = false
  selectedKnowledgeItem.value = null
}

// 处理详情弹窗的编辑操作
const handleDetailEdit = (item) => {
  closeDetailModal()
  editKnowledge(item)
}

// 处理详情弹窗的删除操作
const handleDetailDelete = (id) => {
  closeDetailModal()
  deleteKnowledge(id)
}

// 获取所有标签
const fetchLabelList = async () => {
  try {
    // 从cookie中获取user_id
    const userId = getUserIdFromCookie();
    const response = await request.post('/get_setting/get_label', {
    })
    if (response.data['code'] === 200) {
      labelList.value = response.data['data']
    } else {
      console.error('获取标签失败:', response.msg)
    }
  } catch (err) {
    console.error('获取标签出错:', err)
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchKnowledgeList()
  fetchLabelList()
})

// AI修改相关状态
const showAiEditModal = ref(false);
const aiEditForm = reactive({
  originalContent: '',
  prompt: ''
});

// 提示词相关状态
const promptList = ref([]);
const filteredPromptList = ref([]);
const selectedPromptIds = ref([]);
const filterPromptName = ref('');
const filterPromptType = ref('');
const promptLoading = ref(false);

// 获取提示词列表
const fetchPromptList = async () => {
  try {
    promptLoading.value = true;
    const userId = getUserIdFromCookie();
    const response = await request.post('/get_setting/get_all_prompt', {
      user_id: userId
    });
    
    if (response && response.data && response.data.code === 200) {
      promptList.value = response.data.data || [];
      filteredPromptList.value = [...promptList.value];
    } else {
      console.error('获取提示词列表失败:', response?.data?.msg);
    }
  } catch (error) {
    console.error('请求提示词列表出错:', error);
  } finally {
    promptLoading.value = false;
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

// 打开AI修改弹窗
const openAiEditModal = async () => {
  // 将当前知识内容复制到原文中（不可修改）
  aiEditForm.originalContent = editForm.value.knowledge_content;
  aiEditForm.prompt = ''; // 清空上次的修改意见
  selectedPromptIds.value = []; // 清空上次的选择
  
  // 获取提示词列表
  await fetchPromptList();
  
  showAiEditModal.value = true;
};

// 关闭AI修改弹窗
const closeAiEditModal = () => {
  showAiEditModal.value = false;
};

// 提交AI修改请求
const submitAiEdit = async () => {
  if (!aiEditForm.prompt.trim() && selectedPromptIds.value.length === 0) {
    ElMessage.error('请输入修改意见或选择提示词');
    return;
  }
  
  // 构建完整的提示词
  let fullPrompt = aiEditForm.prompt;
  
  // 将选中的提示词文本拼接到修改意见后
  console.log('选中的提示词ID:', selectedPromptIds.value);
  console.log('提示词列表:', promptList.value);
  
  if (selectedPromptIds.value.length > 0) {
    const selectedPrompts = promptList.value.filter(p => 
      selectedPromptIds.value.includes(p.id)
    );
    
    console.log('筛选后的提示词:', selectedPrompts);
    
    if (selectedPrompts.length > 0) {
        const promptTexts = selectedPrompts.map(p => {
          console.log('提示词对象:', p, 'text属性:', p.text);
          return p.text || '';
        }).join(' ');
      
      console.log('拼接的提示词文本:', promptTexts);
      fullPrompt = fullPrompt ? `${fullPrompt} ${promptTexts}` : promptTexts;
      console.log('拼接后的完整提示词:', fullPrompt);
    }
  }
  
  try {
    ElLoading.service({ text: '正在生成修改内容...' });
    const response = await request.post('/get_knowledge/generate_content_by_ai', {
      knowledge_content: aiEditForm.originalContent,
      prompt: fullPrompt
    });
    console.log('AI修改请求:', fullPrompt);
    
    if (response.data['code'] === 200 && response.data.data?.content) {
      console.log('AI修改内容：'+response.data.data.content)
      // 用AI生成的内容替换知识内容
      editForm.value.knowledge_content = response.data.data.content;
      ElMessage.success('AI修改成功');
      closeAiEditModal();
    } else {
      ElMessage.error('AI修改失败，请重试');
    }
  } catch (error) {
    console.error('AI修改请求失败:', error);
    ElMessage.error('AI修改请求失败，请检查网络或稍后重试');
  } finally {
    ElLoading.service().close();
  }
};
// 组件中添加一个方法来获取类型名称
const getTypeName = (typeId) => {
  const typeMap = {
    1: '文献',
    2: '专利',
    3: '网络信息收藏',
    4: '用户自定义上传文本',
    5: '用户自定义上传文档'
  };
  return typeMap[typeId] || `未知类型(${typeId})`;
};
</script>

<style scoped>
.knowledge-base-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.filter-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 编辑表单样式 */
.edit-form {
  padding: 10px 0;
}

.ai-edit-form {
  padding: 10px 0;
}

.ai-edit-form .form-item {
  margin-bottom: 20px;
}

.prompt-filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.prompt-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background-color: #fafafa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.prompt-loading,
.prompt-empty {
  text-align: center;
  padding: 20px;
  color: #909399;
}

:deep(.el-checkbox) {
  margin-bottom: 8px;
}

.form-item {
  margin-bottom: 20px;
}

.form-label {
  display: inline-block;
  width: 100px;
  font-weight: 500;
  margin-bottom: 8px;
}

.required {
  color: #f56c6c;
}

.dialog-footer {
  text-align: right;
}

.filter-item label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
}

.filter-input,
.el-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
  box-sizing: border-box;
}

.filter-actions-inline {
  display: flex;
  align-items: end;
  padding-left: 8px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.apply-btn {
  background: #1890ff;
  color: white;
}

.apply-btn:hover {
  background: #40a9ff;
}

.reset-btn {
  background: #fff;
  border: 1px solid #d9d9d9;
  color: #666;
}

.reset-btn:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}

/* 标签页样式 */
.label-tabs-container {
  margin: 16px 0;
  padding: 0 0 8px 0;
  border-bottom: 1px solid #e8e8e8;
}

.label-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.label-tab {
  padding: 8px 16px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #666;
  border-radius: 4px 4px 0 0;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border-bottom: 2px solid transparent;
}

.label-tab:hover {
  color: #1890ff;
  border-color: #1890ff;
}

.label-tab.active {
  color: #1890ff;
  background: #fff;
  border-color: #1890ff;
  border-bottom-color: #1890ff;
  position: relative;
  z-index: 1;
}

.label-tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #fff;
}

.data-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-state {
  color: #ff4d4f;
}

.retry-btn {
  margin-left: 10px;
  background: #ff4d4f;
  color: white;
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.data-summary {
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.knowledge-item {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s;
}

.knowledge-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-color: #40a9ff;
}

.item-header {
  margin-bottom: 12px;
}

.item-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.item-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.meta-label {
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 12px;
}

.item-content {
  margin-bottom: 12px;
  color: #666;
  line-height: 1.6;
  font-size: 14px;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.mark-info {
  font-size: 13px;
  color: #1890ff;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
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

.view-btn {
  background: #1890ff;
  color: white;
}

.view-btn:hover {
  background: #40a9ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .filter-item {
    width: 100%;
  }
  
  .filter-input {
    min-width: auto;
    flex: 1;
  }
  
  .item-footer {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .item-actions {
    width: 100%;
    justify-content: space-between;
  }
}
</style>