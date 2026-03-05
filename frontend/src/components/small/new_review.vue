<template>
  <div class="new-review-container">
    <h2 class="title">新建报告</h2>
    
    <div class="form-content">
      <!-- 新建方式选择 -->
      <div class="form-group">
        <label class="form-label">新建方式：</label>
        <div class="radio-group">
          <label class="radio-item">
            <input 
              type="radio" 
              v-model="createType" 
              value="blank" 
              @change="onCreateTypeChange"
            >
            <span>新建空白报告</span>
          </label>
          <label class="radio-item">
            <input 
              type="radio" 
              v-model="createType" 
              value="template" 
              @change="onCreateTypeChange"
            >
            <span>从模板新建</span>
          </label>
        </div>
      </div>
      
      <!-- 报告标题 -->
      <div class="form-group">
        <label class="form-label required">报告标题：</label>
        <input 
          type="text" 
          class="form-input" 
          v-model="reportTitle"
          placeholder="请输入报告标题"
        >
      </div>
      
      <!-- 模板选择（仅在从模板新建时显示） -->
      <div class="form-group" v-if="createType === 'template'">
        <label class="form-label required">选择模板：</label>
        <div v-if="loadingTemplates" class="loading-state">
          <Loading class="loading-icon" />
          <span>加载模板中...</span>
        </div>
        <select 
          v-else 
          class="form-select" 
          v-model="selectedTemplate"
          placeholder="请选择模板"
        >
          <option value="" disabled>请选择模板</option>
          <option 
            v-for="template in templates" 
            :key="template.id" 
            :value="template.id"
          >
            {{ template.name }}
          </option>
        </select>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button 
          class="btn btn-primary" 
          @click="submitForm" 
          :disabled="submitting"
        >
          <span v-if="!submitting">创建报告</span>
          <span v-else>
            <Loading class="loading-icon" />
            创建中...
          </span>
        </button>
        <button 
          class="btn btn-secondary" 
          @click="cancelForm" 
          :disabled="submitting"
        >
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import request from '@/api/request' // 假设项目中有统一的请求工具
import { getUserIdFromCookie } from '@/utils/authUtils' // 导入获取用户ID的工具

// 定义事件
const emit = defineEmits(['close', 'success'])

const router = useRouter()

// 响应式数据
const createType = ref('blank') // blank: 新建空白, template: 从模板新建
const reportTitle = ref('')
const templates = ref([])
const selectedTemplate = ref('')
const loadingTemplates = ref(false)
const submitting = ref(false)

// 监听创建类型变化
const onCreateTypeChange = () => {
  // 重置选择的模板
  selectedTemplate.value = ''
  
  // 如果选择从模板新建，则加载模板列表
  if (createType.value === 'template') {
    loadUserTemplates()
  }
}

// 加载用户模板
const loadUserTemplates = async () => {
  loadingTemplates.value = true
  try {
    // 获取用户ID
    const userId = getUserIdFromCookie();
    
    // 调用接口获取当前用户的所有模板
    const response = await request.post('/get_review/get_all_template', {
      user_id: userId
    });
    
    // 正确处理返回数据格式 {code:200, msg:'success', data: []}
    if (response.data.code === 200) {
      templates.value = response.data.data || [];
      
      // 如果没有模板，给用户提示
      if (templates.value.length === 0) {
        ElMessage.warning('您当前没有可用的模板，请先创建模板或选择新建空白报告');
      }
    } else {
      ElMessage.warning(response.data.msg || '获取模板失败');
      templates.value = [];
    }
  } catch (error) {
    console.error('加载模板失败:', error);
    ElMessage.error('加载模板失败，请稍后重试');
    templates.value = [];
  } finally {
    loadingTemplates.value = false
  }
};

// 表单验证
const validateForm = () => {
  if (!reportTitle.value.trim()) {
    ElMessage.warning('请输入报告标题')
    return false
  }
  
  if (createType.value === 'template' && !selectedTemplate.value) {
    ElMessage.warning('请选择一个模板')
    return false
  }
  
  return true
}

// 提交表单
const submitForm = async () => {
  if (!validateForm()) {
    return
  }
  
  const userId = getUserIdFromCookie()
  if (!userId) {
    ElMessage.error('用户未登录，请重新登录')
    return
  }
  
  submitting.value = true
  try {
    // 准备基础提交数据
    const baseData = {
      user_id: userId,
      title: reportTitle.value.trim()
    }
    
    let submitData = baseData;
    let apiPath = '/get_review/create_review'; // 默认接口
    
    // 根据创建类型选择不同的接口和参数
    if (createType.value !== 'blank' && selectedTemplate.value) {
      apiPath = '/get_review/create_review_by_template';
      submitData = {
        ...baseData,
        template_id: selectedTemplate.value
      };
    }

    // 调用相应的接口创建报告
    const response = await request.post(apiPath, submitData);
    
    // 检查响应
    if (response.data.code === 200) {
      ElMessage.success('报告创建成功');
      emit('success');
      emit('close'); // 关闭当前窗口
    } else {
      ElMessage.warning(response.data.msg || '报告创建失败，请稍后重试');
    }
  } catch (error) {
    console.error('创建报告失败:', error)
    ElMessage.error('创建报告失败，请稍后重试')
  } finally {
    submitting.value = false
  }
};

// 取消表单
const cancelForm = () => {
  // 发出close事件给父组件
  emit('close')
}

// 组件挂载时，如果默认是模板方式，加载模板
onMounted(() => {
  if (createType.value === 'template') {
    loadUserTemplates()
  }
});
</script>

<style scoped>
.new-review-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.title {
  text-align: center;
  margin-bottom: 20px;
  color: #303133;
  font-size: 20px;
  font-weight: 500;
}

.form-content {
  padding: 10px 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  color: #606266;
  font-weight: 500;
}

.form-label.required::after {
  content: '*';
  color: #f56c6c;
  margin-left: 4px;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.radio-item input[type="radio"] {
  margin-right: 6px;
}

.form-input, .form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #409eff;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  color: #909399;
}

.loading-icon {
  margin-right: 8px;
  animation: rotating 1s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
}

.btn {
  padding: 8px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  min-width: 80px;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-primary:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f4f4f5;
  color: #606266;
}

.btn-secondary:hover {
  background-color: #e6e6e6;
}

.btn-secondary:disabled {
  background-color: #f4f4f5;
  color: #c0c4cc;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .new-review-container {
    margin: 10px;
    padding: 15px;
  }
  
  .radio-group {
    flex-direction: column;
    gap: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 200px;
  }
}
</style>