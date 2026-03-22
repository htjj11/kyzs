<template>
  <div class="review-records-container">
    <!-- 顶部标题与操作栏 -->
    <div class="page-header">
      <div class="header-title">
        <el-icon class="title-icon">
          <Document />
        </el-icon>
        <h2>报告记录管理</h2>
      </div>
      <div class="header-actions">
        <!-- 新增：新建空白报告按钮 -->
        <el-button type="primary" class="new-report-btn square-btn" @click="showNewReviewDialog = true">
          <el-icon style="margin-right: 4px">
            <Plus />
          </el-icon>新建空白报告
        </el-button>
      </div>
    </div>

    <!-- 数据表格区域 -->
    <div class="data-section">
      <el-table v-loading="loading" :data="tableData" style="width: 100%" border stripe size="large"
        class="scientific-table">
        <el-table-column prop="id" label="ID" width="100" align="center" />
        <el-table-column prop="title" label="报告主题" min-width="400" show-overflow-tooltip>
          <template #default="scope">
            <span class="report-title">{{ scope.row.title || '无标题' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="正文预览" min-width="250" show-overflow-tooltip>
          <template #default="scope">
            <span style="color: #606266; font-size: 13px;">
              {{ scope.row.review_body ? scope.row.review_body.replace(/<[^>]+>/g, '').substring(0, 100) + '...' : '无内容'
                }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button type="primary" plain size="small" class="square-btn" @click="handleDetail(scope.row)">
              <el-icon>
                <View />
              </el-icon> 详情
            </el-button>
            <el-button type="warning" plain size="small" class="square-btn" @click="handleEdit(scope.row)">
              <el-icon>
                <Edit />
              </el-icon> 编辑
            </el-button>
            <el-button type="danger" plain size="small" class="square-btn" @click="handleDelete(scope.row)">
              <el-icon>
                <Delete />
              </el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="dialogVisible" title="报告详情" :width="'100%'" :fullscreen="true" destroy-on-close
      class="square-dialog detail-dialog">
      <div class="detail-container">
        <!-- 头部信息 -->
        <div class="detail-header-card">
          <h2 class="detail-title">{{ currentRecord.title || '无标题' }}</h2>
          <div class="detail-meta">
            <div class="meta-item"><span class="meta-label">ID:</span> <span class="meta-value">{{ currentRecord.id
                }}</span></div>
            <div class="meta-item"><span class="meta-label">用户ID:</span> <span class="meta-value">{{
              currentRecord.user_id
                }}</span></div>
            <div class="meta-item"><span class="meta-label">标签ID:</span> <span class="meta-value">{{
              currentRecord.label_id
                }}</span></div>
            <div class="meta-item">
              <span class="meta-label">状态:</span>
              <el-tag :type="currentRecord.completion_status === 1 ? 'success' : 'info'" size="small" class="square-tag"
                effect="plain">
                {{ currentRecord.completion_status === 1 ? '已完成' : '未完成' }}
              </el-tag>
            </div>
          </div>
          <div class="detail-actions">
            <el-button type="primary" class="square-btn" @click="downloadWord(currentRecord.id)">
              <el-icon style="margin-right: 4px">
                <Download />
              </el-icon> 导出 Word 文档
            </el-button>
          </div>
        </div>

        <!-- 正文信息 -->
        <div class="detail-body-card">
          <div class="section-title">报告正文区</div>
          <div class="review-body-wrapper">
            <div class="review-body" v-html="currentRecord.review_body || '<div class=\'empty-content\'>无内容</div>'">
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button class="square-btn" @click="dialogVisible = false">关闭窗口</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑报告" :width="'100%'" :height="'100%'" :fullscreen="true"
      :modal="false" @close="handleEditDialogClose" class="square-dialog">
      <NewEditor v-if="editDialogVisible" :review-id="currentRecord.id" :review-data="currentRecord"
        @close="editDialogVisible = false" @saved="handleSaveSuccess" />
    </el-dialog>

    <!-- 新建报告弹窗 -->
    <el-dialog v-model="showNewReviewDialog" title="新建空白报告" :width="'600px'" top="10vh" class="square-dialog">
      <NewReview @close="handleNewReviewClose" />
    </el-dialog>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElTable, ElTableColumn, ElButton, ElDialog, ElTag, ElMessage, ElMessageBox, ElInput, ElIcon } from 'element-plus';
import { Document, Plus, View, Edit, Delete, Download } from '@element-plus/icons-vue';
import request from '@/api/request';
import { getUserIdFromCookie } from '@/utils/authUtils';

import NewReview from '../small/new_review.vue';
import NewEditor from './new_editor.vue';

const tableData = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const editDialogVisible = ref(false);
const showNewReviewDialog = ref(false);

const currentRecord = ref({});

const showEditInput = ref(false);
const selectedText = ref('');
const replacedText = ref('');
const editLoading = ref(false);

const handleNewReviewClose = () => {
  showNewReviewDialog.value = false;
  fetchReviewRecords();
};

const handleEdit = (row) => {
  currentRecord.value = { ...row };
  editDialogVisible.value = true;
  showEditInput.value = false;
  selectedText.value = '';
  replacedText.value = '';
  console.log(currentRecord.value);
};

const handleEditDialogClose = () => {
  console.log('编辑弹窗已关闭');
  fetchReviewRecords();
};

const handleSaveSuccess = () => {
  fetchReviewRecords();
};

const handleReviewUpdate = (newData) => {
  console.log('Review updated:', newData);
  fetchReviewRecords();
};

const fetchReviewRecords = async () => {
  try {
    loading.value = true;
    const userId = getUserIdFromCookie();
    const response = await request.post('/get_review/get_all_review', { user_id: userId });
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

const handleDetail = (row) => {
  currentRecord.value = { ...row };
  dialogVisible.value = true;
};

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      '您真的要这么做吗？删除后将无法恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
  } catch {
    // 用户取消了删除
    return;
  }

  try {
    const response = await request.post('/get_review/delete_review', { review_id: row.id });
    if (response.data && response.data.code === 200 && response.data.msg === 'success') {
      ElMessage.success(response.data.msg || '删除成功');
      fetchReviewRecords();
    } else {
      ElMessage.error(response.data?.msg || '删除失败');
    }
  } catch (error) {
    ElMessage.error('删除失败: ' + (error.message || '未知错误'));
    console.error('Error deleting review record:', error);
  }
};

const downloadWord = async (id) => {
  try {
    const response = await request.post('/get_review/get_review_fuwenben_base64', { review_id: id });

    if (response.data.code !== 200) {
      throw new Error(response.data.msg || '下载失败');
    }

    let base64Data = response.data.data;
    console.log('接收原始响应数据:', response.data);

    if (typeof base64Data === 'object' && base64Data !== null && base64Data.data) {
      console.log('检测到嵌套数据结构，提取内层data');
      base64Data = base64Data.data;
    }

    if (typeof base64Data !== 'string') {
      console.warn('base64Data不是字符串，尝试转换', typeof base64Data);
      base64Data = String(base64Data);
    }

    console.log('处理后的base64Data长度:', base64Data.length);

    try {
      const binaryString = atob(base64Data);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const blob = new Blob([bytes], {
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
      });

      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `summary_${id}.docx`;
      link.click();

      URL.revokeObjectURL(url);
      ElMessage.success('下载成功');
    } catch (atobError) {
      console.error('base64解码错误:', atobError);
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
/* =========== 整体页面布局 =========== */
.review-records-container {
  padding: 24px;
  background-color: #f4f6f8;
  /* 偏科研严谨的淡灰偏蓝背景 */
  min-height: calc(100vh - 56px);
  box-sizing: border-box;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

/* =========== 顶部操作栏 =========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding: 16px 24px;
  margin-bottom: 20px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 1px;
}

.title-icon {
  font-size: 22px;
  color: #3f88f2;
}

/* =========== 核心方正风格控件 =========== */
.square-btn {
  border-radius: 2px !important;
  font-weight: 500;
  letter-spacing: 1px;
}

.square-tag {
  border-radius: 2px !important;
  font-weight: bold;
}

/* =========== 数据表格区域 =========== */
.data-section {
  background: #ffffff;
  padding: 24px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.scientific-table {
  border: 1px solid #dcdfe6;
}

:deep(.scientific-table th.el-table__cell) {
  background-color: #f5f7fa !important;
  color: #606266;
  font-weight: 600;
  border-bottom: 2px solid #e4e7ed;
}

.report-title {
  font-weight: 500;
  color: #303133;
}

/* =========== 弹窗方正样式覆盖 =========== */
:deep(.square-dialog .el-dialog) {
  border-radius: 2px;
}

:deep(.square-dialog .el-dialog__header) {
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  margin-right: 0;
  padding: 16px 24px;
}

:deep(.square-dialog .el-dialog__title) {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

/* =========== 详情弹窗专属样式 =========== */
.detail-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: #f4f6f8;
  padding: 24px;
  min-height: calc(100vh - 150px);
}

.detail-header-card {
  background: #ffffff;
  padding: 24px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
}

.detail-title {
  margin: 0 0 16px 0;
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 16px;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.meta-label {
  color: #909399;
  font-weight: 500;
}

.meta-value {
  color: #303133;
  font-weight: 600;
}

.detail-actions {
  display: flex;
}

.detail-body-card {
  background: #ffffff;
  padding: 24px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  border-left: 4px solid #3f88f2;
  padding-left: 10px;
}

.review-body-wrapper {
  flex: 1;
  background-color: #fafbfc;
  border: 1px solid #dcdfe6;
  border-radius: 2px;
  padding: 24px;
  overflow-y: auto;
}

.review-body {
  font-family: 'Times New Roman', SimSun, 'Songti SC', serif;
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
}

.review-body p {
  margin-top: 0.8em;
  margin-bottom: 0.8em;
  text-align: justify;
}

/* 富文本内容基础样式 */
.review-body h1,
.review-body h2,
.review-body h3,
.review-body h4,
.review-body h5,
.review-body h6 {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', sans-serif;
  color: #1f2f3f;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  font-weight: 600;
}

.review-body h1 {
  font-size: 24px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.review-body h2 {
  font-size: 20px;
}

.review-body h3 {
  font-size: 18px;
}

.review-body strong,
.review-body b {
  font-weight: 600;
  color: #1f2f3f;
}

.review-body ul,
.review-body ol {
  padding-left: 2em;
  margin-bottom: 1em;
}

.review-body li {
  margin-bottom: 0.5em;
}

.review-body blockquote {
  border-left: 4px solid #c0c4cc;
  padding-left: 16px;
  margin-left: 0;
  color: #606266;
  background-color: #f8f9fa;
  padding: 12px 16px;
  margin: 1em 0;
}

.review-body hr {
  border: none;
  border-top: 1px solid #dcdfe6;
  margin: 2em 0;
}

.review-body code {
  background-color: #f4f4f5;
  padding: 2px 6px;
  border-radius: 2px;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 0.9em;
  color: #e65c5c;
}

.review-body pre {
  background-color: #282c34;
  color: #abb2bf;
  padding: 16px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 1em 0;
  font-family: 'Consolas', 'Courier New', monospace;
}

.review-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

.review-body th,
.review-body td {
  border: 1px solid #dcdfe6;
  padding: 12px;
}

.review-body th {
  background-color: #f5f7fa;
  font-weight: 600;
}
</style>