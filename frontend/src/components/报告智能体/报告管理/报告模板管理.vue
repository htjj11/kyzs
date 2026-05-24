<template>
  <div class="template-manager-container">
    <!-- 顶部操作栏 -->
    <div class="manager-toolbar">
      <button class="btn btn-primary" @click="openCreateDialog">
        + 新建模板
      </button>
    </div>

    <!-- 模板列表 -->
    <div class="template-list" v-if="!loading">
      <div v-if="templates.length === 0" class="empty-state">
        暂无模板，点击「新建模板」创建一个
      </div>
      <div
        v-for="tpl in templates"
        :key="tpl.id"
        class="template-card"
      >
        <div class="template-card-info">
          <span class="template-name">{{ tpl.name || '未命名模板' }}</span>
          <span class="template-id">ID: {{ tpl.id }}</span>
        </div>
        <div class="template-card-actions">
          <button class="btn btn-sm btn-edit" @click="openEditDialog(tpl)">编辑</button>
          <button class="btn btn-sm btn-danger" @click="confirmDelete(tpl)">删除</button>
        </div>
      </div>
    </div>

    <div v-else class="loading-state">
      加载中...
    </div>

    <!-- 新建/编辑模板弹窗（全屏，使用 TinyMCE 富文本编辑器） -->
    <el-dialog
      v-model="showEditorDialog"
      :title="editingTemplate ? '编辑模板' : '新建模板'"
      :fullscreen="true"
      append-to-body
      destroy-on-close
      class="square-dialog template-editor-dialog"
    >
      <NewEditor
        v-if="showEditorDialog"
        :review-id="editingTemplate ? editingTemplate.id : null"
        :review-data="editingTemplate"
        mode="template"
        @close="showEditorDialog = false"
        @saved="handleSaveSuccess"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/api/request'
import { getUserIdFromCookie } from '@/utils/authUtils'
import NewEditor from './报告编辑器.vue'

const emit = defineEmits(['updated'])

const templates = ref([])
const loading = ref(false)

// 编辑/新建弹窗状态
const showEditorDialog = ref(false)
const editingTemplate = ref(null) // null 代表新建

// 加载模板列表
const loadTemplates = async () => {
  loading.value = true
  try {
    const userId = getUserIdFromCookie()
    const response = await request.post('/report/get_all_template', { user_id: userId })
    if (response.data.code === 200) {
      templates.value = response.data.data || []
    } else {
      ElMessage.warning(response.data.msg || '获取模板失败')
      templates.value = []
    }
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败，请稍后重试')
    templates.value = []
  } finally {
    loading.value = false
  }
}

// 打开新建弹窗（editingTemplate 为 null，编辑器内容为空）
const openCreateDialog = () => {
  editingTemplate.value = null
  showEditorDialog.value = true
}

// 打开编辑弹窗（将模板数据传给编辑器）
const openEditDialog = (tpl) => {
  editingTemplate.value = tpl
  showEditorDialog.value = true
}

// 编辑器保存成功回调
const handleSaveSuccess = async () => {
  showEditorDialog.value = false
  await loadTemplates()
  emit('updated')
}

// 删除确认（需传 user_id 给后端做权限校验）
const confirmDelete = async (tpl) => {
  const displayName = tpl.name || '未命名模板'
  try {
    await ElMessageBox.confirm(
      `确定要删除模板「${displayName}」吗？删除后无法恢复。`,
      '删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }

  try {
    const response = await request.post('/report/delete_template', {
      template_id: tpl.id,
      user_id: getUserIdFromCookie()
    })
    if (response.data && response.data.code === 200) {
      ElMessage.success('模板已删除')
      await loadTemplates()
      emit('updated')
    } else {
      ElMessage.warning(response.data?.msg || '删除失败')
    }
  } catch (error) {
    console.error('删除模板失败:', error)
    ElMessage.error('删除失败，请稍后重试')
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.template-manager-container {
  padding: 4px 0;
  min-height: 200px;
}

.manager-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.template-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.template-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fafafa;
  transition: box-shadow 0.2s;
}

.template-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.template-card-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.template-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.template-id {
  font-size: 12px;
  color: #909399;
}

.template-card-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  color: #909399;
  padding: 40px 0;
  font-size: 14px;
}

.loading-state {
  text-align: center;
  color: #909399;
  padding: 40px 0;
  font-size: 14px;
}

.btn {
  padding: 7px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 13px;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-edit {
  background-color: #e6a23c;
  color: white;
}

.btn-edit:hover {
  background-color: #ebb563;
}

.btn-danger {
  background-color: #f56c6c;
  color: white;
}

.btn-danger:hover {
  background-color: #f78989;
}

/* 全屏弹窗整体走 flex，让 body 自动占满剩余空间 */
:deep(.template-editor-dialog.el-dialog--fullscreen) {
  display: flex;
  flex-direction: column;
}

:deep(.template-editor-dialog .el-dialog__body) {
  flex: 1;
  padding: 0 !important;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 方正风格弹窗 */
:deep(.square-dialog .el-dialog) {
  border-radius: 2px;
}

:deep(.square-dialog .el-dialog__header) {
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  margin-right: 0;
  padding: 14px 24px;
}

:deep(.square-dialog .el-dialog__title) {
  font-weight: 600;
  color: #303133;
}
</style>
