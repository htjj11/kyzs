<template>
  <div class="review-records-container">
    <h1>报告记录管理</h1>
    <!-- 新增：新建空白报告按钮 -->
    <el-button type="primary" class="new-report-btn" @click="showNewReviewDialog = true">
      新建空白报告
    </el-button>
    
    <el-table
      v-loading="loading"
      :data="tableData"
      style="width: 100%"
      border
    >
      <!-- 表格内容保持不变 -->
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="主题" width="500" />
      <el-table-column label="完成状态" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.completion_status === 1 ? 'success' : 'info'">
            {{ scope.row.completion_status === 1 ? '已完成' : '未完成' }}
          </el-tag>
        </template>
      </el-table-column>
  

      <el-table-column label="操作" width="2000">
        <template #default="scope">
          <el-button type="primary" size="small" @click="handleDetail(scope.row)">
            详情
          </el-button>
          <el-button type="info" size="small" @click="handleEdit(scope.row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="报告详情"
      :width="'80%'"
    >
      <div class="detail-container" style="max-height: 60vh; overflow-y: auto;">
        <div class="detail-item">
          <span class="label">ID:</span>
          <span class="value">{{ currentRecord.id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">主题:</span>
          <span class="value">{{ currentRecord.title || '无标题' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">完成状态:</span>
          <span class="value">{{ currentRecord.completion_status === 1 ? '已完成' : '未完成' }}</span>
        </div>
        <div class="detail-item">
          <span class="label">用户ID:</span>
          <span class="value">{{ currentRecord.user_id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">标签ID:</span>
          <span class="value">{{ currentRecord.label_id }}</span>
        </div>
        <div class="detail-item">
          <span class="label">报告正文:</span>
          <div class="review-body">
            {{ currentRecord.review_body || '无内容' }}
          </div>
          <el-button type="primary" size="small" @click="downloadWord(currentRecord.id)">下载Word</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑报告"
      :width="'100%'"
      :height="'100%'"
      @close="handleEditDialogClose"
    >
      <EditReview 
        v-if="editDialogVisible && currentRecord.id" 
        :record="currentRecord" 
        @close="editDialogVisible = false"
        @update:modelValue="handleReviewUpdate"
      />
    </el-dialog>
    
    <!-- 新增：新建报告弹窗 -->
    <el-dialog
      v-model="showNewReviewDialog"
      title="新建报告"
      :width="'600px'"
      top="10vh"
    >
      <NewReview @close="handleNewReviewClose"  />
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElTable, ElTableColumn, ElButton, ElDialog, ElTag, ElMessage, ElInput } from 'element-plus';
import request from '@/api/request';
import { getUserIdFromCookie } from '@/utils/authUtils';
import EditReview from '../small/edit_review.vue';
// 新增：导入NewReview组件
import NewReview from '../small/new_review.vue';

// 响应式数据
const tableData = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editDialogVisible = ref(false);
// 新增：控制新建报告弹窗显示
const showNewReviewDialog = ref(false);

const currentRecord = ref({});

// 新增：文本编辑相关状态
const showEditInput = ref(false);
const selectedText = ref('');
const replacedText = ref('');
const editLoading = ref(false);

// 新增：处理新建报告弹窗关闭
const handleNewReviewClose = () => {
  showNewReviewDialog.value = false;
  // 刷新数据
  fetchReviewRecords();
};


// 编辑窗口按钮
const handleEdit = (row) => {
  currentRecord.value = { ...row };
  editDialogVisible.value = true;
  // 重置编辑状态
  showEditInput.value = false;
  selectedText.value = '';
  replacedText.value = '';
  console.log(currentRecord.value);
};

// 编辑弹窗关闭处理
const handleEditDialogClose = () => {
  // 这里可以添加弹窗关闭后的清理逻辑
  console.log('编辑弹窗已关闭');
  // 更新记录
  fetchReviewRecords();
};

// 处理Review更新
const handleReviewUpdate = (newData) => {
  // 这里可以根据实际需求处理更新后的数据
  console.log('Review updated:', newData);
  // 重新获取数据以更新列表
  fetchReviewRecords();
};

// 获取综述记录数据
const fetchReviewRecords = async () => {
  try {
    loading.value = true;
    const userId = getUserIdFromCookie();
    const response = await request.post('/get_review/get_all_review', { user_id: userId });
    // 检查响应状态和数据格式
    if (response && response.data && response.data.code === 200) {
      tableData.value = response.data.data;
    } else {
      throw new Error(response?.data?.msg || '获取数据失败');
    }
  } catch (error) {
    ElMessage.error('获取数据失败: ' + (error.message || '未知错误'));
    console.error('Error fetching review records:', error);
  } finally {
    loading.value = false;
  }
};

// 处理详情查看
const handleDetail = (row) => {
  currentRecord.value = { ...row };
  dialogVisible.value = true;
};

// 处理删除操作
const handleDelete = async (row) => {
  try {
    // 调用新的删除接口，使用正确的参数格式
    const response = await request.post('/get_review/delete_review', { review_id: row.id });
    
    // 检查响应格式，根据之前的模式使用response.data
    if (response.data && response.data.code === 200 && response.data.msg === 'success') {
      ElMessage.success(response.data.msg || '删除成功');
      fetchReviewRecords(); // 删除成功后刷新列表
    } else {
      ElMessage.error(response.data?.msg || '删除失败');
    }
  } catch (error) {
    ElMessage.error('删除失败: ' + (error.message || '未知错误'));
    console.error('Error deleting review record:', error);
  }
};

// 下载Word文档，接口返回的是{'code': 200, 'msg': 'success', 'data': 'UEsDBBQAAggIAJKBA1sIaLrOgwEAAI0HAAATAAAAW0NvbnRlbnRfVHlwZXNdLnhtbLWVy07DMBBFfyXKFiVuWSCE'}，要将data内的内容转为文件
const downloadWord = async (id) => {
  try {
    const response = await request.post('/get_review/get_review_base64', { review_id: id});
  
    // 检查响应状态
    if (response.data.code !== 200) {
      throw new Error(response.data.msg || '下载失败');
    }
    
    // 获取嵌套的base64数据
    let base64Data = response.data.data;
    console.log('接收原始响应数据:', response.data);
    
    // 检查数据是否嵌套了多层
    if (typeof base64Data === 'object' && base64Data !== null && base64Data.data) {
      console.log('检测到嵌套数据结构，提取内层data');
      base64Data = base64Data.data;
    }
    
    // 确保是字符串格式
    if (typeof base64Data !== 'string') {
      console.warn('base64Data不是字符串，尝试转换', typeof base64Data);
      base64Data = String(base64Data);
    }
    
    console.log('处理后的base64Data长度:', base64Data.length);
    
    try {
      // 将base64转换为二进制数据
      const binaryString = atob(base64Data);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // 创建Blob对象
      const blob = new Blob([bytes], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      });
      
      // 创建下载链接
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `summary_${id}.docx`;
      link.click();
      
      // 释放URL对象
      URL.revokeObjectURL(url);
      
      ElMessage.success('下载成功');
    } catch (atobError) {
      console.error('base64解码错误:', atobError);
      // 尝试另一种方式处理，比如直接提供原始数据链接
      ElMessage.error('文档解码失败，请检查数据格式');
    }
  } catch (error) {
    ElMessage.error('下载失败: ' + (error.message || '未知错误'));
    console.error('Error downloading word document:', error);
  }
};

onMounted(() => {
  fetchReviewRecords();
});
</script>

<style scoped>
.review-records-container {
  padding: 20px;
}

/* 新增：新建报告按钮样式 */
.new-report-btn {
  margin-bottom: 20px;
}

.detail-container {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-item {
  margin-bottom: 16px;
}

.label {
  font-weight: bold;
  display: inline-block;
  width: 160px;
  vertical-align: top;
}

.json-content pre {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.review-body {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.6;
}
.detail-container {
  max-height: 70vh;
  overflow: hidden;
}

.edit-layout {
  display: flex;
  height: 60vh;
  gap: 20px;
}

/* 左侧内容区域 */
.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #fafafa;
  border-radius: 4px;
  padding: 16px;
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
}

.review-body.scrollable:hover {
  background-color: #f9f9f9;
}

/* 右侧编辑区域 */
.edit-section {
  width: 400px;
  display: flex;
  flex-direction: column;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .edit-layout {
    flex-direction: column;
    height: 70vh;
  }
  
  .edit-section {
    width: 100%;
    height: 300px;
  }
}

@media (max-width: 768px) {
  .el-dialog {
    width: 95% !important;
    margin: 20px auto !important;
  }
  
  .detail-container {
    max-height: 80vh;
  }
  
  .edit-layout {
    height: 60vh;
  }
}
</style>