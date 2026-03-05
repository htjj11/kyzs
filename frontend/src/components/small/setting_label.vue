<template>
  <div class="label-setting-container">
    <div class="label-setting-header">
      <div style="display: flex; align-items: center;">
        <h3>标签管理</h3>
        <el-tooltip content="这是知识库内容的标签，可以将不同内容放到不同的标签下，方便管理和检索" placement="top">
          <span style="margin-left: 8px; cursor: help; color: #909399; font-size: 16px;">?</span>
        </el-tooltip>
      </div>
      <el-button type="primary" @click="showAddDialog">添加标签</el-button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filter-container">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索标签名称"
        clearable
        style="width: 200px; margin-right: 12px;"
        @clear="getAllLabels"
        @keyup.enter="getAllLabels"
      />
      <el-button type="primary" @click="getAllLabels">搜索</el-button>
    </div>

    <!-- 标签列表 -->
    <div class="label-list-container">
      <el-table
        v-loading="loading"
        :data="labelList"
        style="width: 100%"
        border
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="label_name" label="标签名称" width="180" />
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

    <!-- 添加/编辑标签对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="400px"
      @close="resetForm"
    >
      <el-form ref="labelFormRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入标签名称" />
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
import { ElMessage, ElMessageBox, ElTooltip } from 'element-plus';
import axios from '@/api/request';


const loading = ref(false);
const labelList = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const searchKeyword = ref('');

// 对话框相关状态
const dialogVisible = ref(false);
const dialogTitle = ref('添加标签');
const labelFormRef = ref(null);
const formData = reactive({
  id: '',
  name: ''
});

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' },
    { min: 1, max: 50, message: '名称长度在 1 到 50 个字符', trigger: 'blur' }
  ]
};

// 获取所有标签
const getAllLabels = async () => {
  try {
    loading.value = true;

    const response = await axios.post('/get_setting/get_label', {});
    if (response && response.data && response.data.code === 200) {
      // 先保存完整的原始数据
      let allLabels = response.data.data || [];

      // 在本地进行筛选
      if (searchKeyword.value) {
        const keyword = searchKeyword.value.toLowerCase();
        allLabels = allLabels.filter(label => 
          label.label_name.toLowerCase().includes(keyword)
        );
      }
      
      // 计算总数
      total.value = allLabels.length;
      
      // 本地分页处理
      const startIndex = (currentPage.value - 1) * pageSize.value;
      const endIndex = startIndex + pageSize.value;
      labelList.value = allLabels.slice(startIndex, endIndex);
    } else {
      labelList.value = [];
      total.value = 0;
      ElMessage.error(response?.data?.msg || '获取标签列表失败');
    }
  } catch (error) {
    labelList.value = [];
    total.value = 0;
    ElMessage.error('获取标签列表失败: ' + (error.message || '未知错误'));
    console.error('Error getting label list:', error);
  } finally {
    loading.value = false;
  }
};

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加标签';
  resetForm();
  dialogVisible.value = true;
};

// 显示编辑对话框
const showEditDialog = (row) => {
  dialogTitle.value = '编辑标签';
  // 复制数据到表单
  formData.id = row.id;
  formData.name = row.label_name;
  dialogVisible.value = true;
};

// 重置表单
const resetForm = () => {
  formData.id = '';
  formData.name = '';
  if (labelFormRef.value) {
    labelFormRef.value.resetFields();
  }
};

// 提交表单
const submitForm = async () => {
  if (!labelFormRef.value) return;
  
  try {
    await labelFormRef.value.validate();
    
    let response;
    if (formData.id) {
      // 编辑操作
      response = await axios.post('/update_label', {
        id: Number(formData.id),
        label_name: formData.name,

      });
    } else {
      // 添加操作
      response = await axios.post('/get_setting/add_label', {
        label_name: formData.name
      });
    }
    
    if (response && response.data && response.data.code === 200) {
      ElMessage.success(formData.id ? '编辑成功' : '添加成功');
      dialogVisible.value = false;
      getAllLabels(); // 重新获取列表
    } else {
      throw new Error(response?.data?.msg || (formData.id ? '编辑失败' : '添加失败'));
    }
  } catch (error) {
    ElMessage.error(error.message || '操作失败');
    console.error('Error submitting form:', error);
  }
};

// 删除标签
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个标签吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    const response = await axios.post('/get_setting/delete_label', {    
      id: Number(id)
    });
    
    if (response && response.data && response.data.code === 200) {
      ElMessage.success('删除成功');
      getAllLabels(); // 重新获取列表
    } else {
      throw new Error(response?.data?.msg || '删除失败');
    }
  } catch (error) {
    // 用户取消删除也会进入catch，不显示错误
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败');
      console.error('Error deleting label:', error);
    }
  }
};

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size;
  getAllLabels();
};

const handleCurrentChange = (current) => {
  currentPage.value = current;
  getAllLabels();
};

// 初始化数据
onMounted(() => {
  getAllLabels();
});
</script>

<style scoped>
.label-setting-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.label-setting-header {
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

.label-list-container {
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