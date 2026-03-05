<template>
  <div class="prompt-setting-container">
    <div class="prompt-setting-header">
      <h3>提示词设置</h3>
      <el-button type="primary" @click="showAddDialog">添加提示词</el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filter-container">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索提示词名称"
        clearable
        style="width: 200px; margin-right: 12px;"
        @clear="getAllPrompts"
        @keyup.enter="getAllPrompts"
      />
      <el-select
          v-model="filterType"
          placeholder="筛选类型"
          clearable
          style="width: 120px; margin-right: 12px;"
          @change="getAllPrompts"
        >
          <el-option label="全部" value="" />
          <el-option v-for="type in promptTypes" :key="type.id" :label="type.type_name" :value="type.id" />
        </el-select>
      <el-button type="primary" @click="getAllPrompts">搜索</el-button>
    </div>

    <!-- 提示词列表 -->
    <div class="prompt-list-container">
      <el-table
        v-loading="loading"
        :data="promptList"
        style="width: 100%"
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="text" label="提示词内容" min-width="300" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="scope">
            {{ promptTypeMap[scope.row.type] || '未知类型' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="showEditDialog(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 添加/编辑提示词对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="resetForm"
    >
      <el-form ref="promptFormRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入提示词名称" />
        </el-form-item>
        <el-form-item label="内容" prop="text">
          <el-input
            v-model="formData.text"
            type="textarea"
            :rows="4"
            placeholder="请输入提示词内容"
          />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="formData.type" placeholder="请选择提示词类型">
            <el-option v-for="type in promptTypes" :key="type.id" :label="type.type_name" :value="String(type.id)" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '@/api/request';
import { getUserIdFromCookie } from '@/utils/authUtils';

// 状态定义
const loading = ref(false);
const promptList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const searchKeyword = ref('');
const filterType = ref('');
// 提示词类型列表和映射
const promptTypes = ref([]);
const promptTypeMap = ref({});

// 对话框相关状态
const dialogVisible = ref(false);
const dialogTitle = ref('添加提示词');
const promptFormRef = ref(null);
const formData = reactive({
  id: '',
  name: '',
  text: '',
  type: '1'
});

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入提示词名称', trigger: 'blur' },
    { min: 1, max: 50, message: '名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  text: [
    { required: true, message: '请输入提示词内容', trigger: 'blur' },
    { min: 1, max: 500, message: '内容长度在 1 到 500 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择提示词类型', trigger: 'change' }
  ]
};

// 获取用户ID
const getUserId = () => {
  return getUserIdFromCookie() || '';
};

// 获取所有提示词类型
const getAllPromptTypes = async () => {
  try {
    const userId = getUserId();
    const response = await request.post('/get_setting/get_all_prompt_type', {
      user_id: userId
    });
    
    if (response && response.data && response.data.code === 200) {
      promptTypes.value = response.data.data || [];
      // 构建类型映射
      promptTypeMap.value = {};
      promptTypes.value.forEach(type => {
        promptTypeMap.value[type.id] = type.type_name;
      });
      return true;
    } else {
      promptTypes.value = [];
      promptTypeMap.value = {};
      ElMessage.warning('获取提示词类型失败: ' + (response?.data?.msg || '未知错误'));
      return false;
    }
  } catch (error) {
    promptTypes.value = [];
    promptTypeMap.value = {};
    console.error('Error getting prompt types:', error);
    return false;
  }
};

// 获取所有提示词 - 只传入user_id，其他筛选在本地实现
const getAllPrompts = async () => {
  try {
    loading.value = true;
    
    // 并行调用两个接口
    const userId = getUserId();
    const [promptResponse, typesSuccess] = await Promise.all([
      request.post('/get_setting/get_all_prompt', { user_id: userId }),
      getAllPromptTypes()
    ]);
    
    if (promptResponse && promptResponse.data && promptResponse.data.code === 200) {
      // 先保存完整的原始数据
      const allPrompts = promptResponse.data.data || [];

      
      // 在本地进行筛选
      let filteredPrompts = [...allPrompts];
      
      // 根据关键词筛选
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase();
        filteredPrompts = filteredPrompts.filter(prompt => 
          prompt.name.toLowerCase().includes(keyword) || 
          prompt.text.toLowerCase().includes(keyword)
        );
      }
      
      // 根据类型筛选
      if (filterType.value) {
        filteredPrompts = filteredPrompts.filter(prompt => 
          prompt.type === Number(filterType.value)
        );
      }
      
      // 计算总数
      total.value = filteredPrompts.length;
      
      // 本地分页处理
      const startIndex = (currentPage.value - 1) * pageSize.value;
      const endIndex = startIndex + pageSize.value;
      promptList.value = filteredPrompts.slice(startIndex, endIndex);
    } else {
      promptList.value = [];
      total.value = 0;
      ElMessage.error(promptResponse?.data?.msg || '获取提示词列表失败');
    }
  } catch (error) {
    promptList.value = [];
    total.value = 0;
    ElMessage.error('获取提示词列表失败: ' + (error.message || '未知错误'));
    console.error('Error getting prompt list:', error);
  } finally {
    loading.value = false;
  }
};

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加提示词';
  resetForm();
  dialogVisible.value = true;
};

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogTitle.value = '编辑提示词';
  // 复制数据到表单
  formData.id = row.id;
  formData.name = row.name;
  formData.text = row.text;
  formData.type = String(row.type);
  dialogVisible.value = true;
};

// 重置表单
const resetForm = () => {
  formData.id = '';
  formData.name = '';
  formData.text = '';
  formData.type = '1';
  if (promptFormRef.value) {
    promptFormRef.value.resetFields();
  }
};

// 提交表单
const submitForm = async () => {
  if (!promptFormRef.value) return;
  
  try {
    await promptFormRef.value.validate();
    
    const userId = getUserId();
    if (!userId) {
      ElMessage.error('请先登录');
      return;
    }
    
    let response;
    if (formData.id) {
      // 编辑操作 - 根据接口定义，参数需要单独提交
      response = await request.post('/get_setting/update_prompt', {
        name: formData.name,
        text: formData.text,
        type: Number(formData.type), // 确保类型ID是数字
        id: Number(formData.id) // 确保提示词ID是数字
      });
    } else {
      // 添加操作 - 根据接口定义，参数需要单独提交
      response = await request.post('/get_setting/add_prompt', {
        user_id: userId,
        name: formData.name,
        text: formData.text,
        type: Number(formData.type) // 确保类型ID是数字
      });
    }
    
    if (response && response.data && response.data.code === 200) {
      ElMessage.success(formData.id ? '编辑成功' : '添加成功');
      dialogVisible.value = false;
      getAllPrompts(); // 重新获取列表
    } else {
      throw new Error(response?.data?.msg || (formData.id ? '编辑失败' : '添加失败'));
    }
  } catch (error) {
    ElMessage.error(error.message || '操作失败');
    console.error('Error submitting form:', error);
  }
};

// 删除提示词
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个提示词吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    // 根据接口定义，确保id是数字类型
    const response = await request.post('/get_setting/delete_prompt', {
      id: Number(id)
    });
    
    if (response && response.data && response.data.code === 200) {
      ElMessage.success('删除成功');
      getAllPrompts(); // 重新获取列表
    } else {
      throw new Error(response?.data?.msg || '删除失败');
    }
  } catch (error) {
    // 用户取消删除也会进入catch，不显示错误
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败');
      console.error('Error deleting prompt:', error);
    }
  }
};

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size;
  getAllPrompts();
};

const handleCurrentChange = (current) => {
  currentPage.value = current;
  getAllPrompts();
};

// 初始化数据
onMounted(() => {
  getAllPrompts();
});
</script>

<style scoped>
.prompt-setting-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.prompt-setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-filter-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.prompt-list-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>