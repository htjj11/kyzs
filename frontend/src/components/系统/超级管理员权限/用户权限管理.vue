<template>
  <div class="user-permission-container">
    <!-- 搜索用户区域 -->
    <div class="search-bar">
      <el-input
        v-model="searchUserName"
        placeholder="输入用户名进行查询"
        clearable
        style="width: 300px"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" :loading="searching" @click="handleSearch">查询权限</el-button>
    </div>

    <!-- 当前查询的用户信息 -->
    <div v-if="currentUserName" class="user-section">
      <div class="section-header">
        <span class="user-label">用户：<b>{{ currentUserName }}</b></span>
        <div class="header-actions">
          <el-button
            size="small"
            type="primary"
            plain
            :icon="Plus"
            @click="openAddDialog"
          >新增权限</el-button>
          <el-button
            size="small"
            type="warning"
            plain
            :icon="Edit"
            @click="openSetDialog"
          >批量设置</el-button>
          <el-popconfirm
            title="确定要清空该用户所有权限吗？"
            confirm-button-text="确定清空"
            cancel-button-text="取消"
            @confirm="handleDeleteAll"
          >
            <template #reference>
              <el-button size="small" type="danger" plain :icon="Delete">清空权限</el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>

      <!-- 权限列表 -->
      <el-table
        :data="permissionList"
        v-loading="tableLoading"
        empty-text="该用户暂无权限"
        class="permission-table"
        border
        size="small"
      >
        <el-table-column type="index" label="#" width="55" align="center" />
        <el-table-column prop="permission" label="权限标识" />
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              plain
              @click="openUpdateDialog(row.permission)"
            >修改</el-button>
            <el-popconfirm
              :title="`确定删除权限「${row.permission}」？`"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleDelete(row.permission)"
            >
              <template #reference>
                <el-button size="small" type="danger" plain>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增权限弹窗 -->
    <el-dialog v-model="addDialogVisible" title="新增权限" width="400px" :close-on-click-modal="false">
      <el-form :model="addForm" :rules="addRules" ref="addFormRef" label-position="top">
        <el-form-item label="权限标识" prop="permission">
          <el-input
            v-model="addForm.permission"
            placeholder="如 document:delete"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleAdd">确认新增</el-button>
      </template>
    </el-dialog>

    <!-- 修改权限弹窗 -->
    <el-dialog v-model="updateDialogVisible" title="修改权限" width="400px" :close-on-click-modal="false">
      <el-form :model="updateForm" :rules="updateRules" ref="updateFormRef" label-position="top">
        <el-form-item label="原权限标识">
          <el-input v-model="updateForm.permission" disabled />
        </el-form-item>
        <el-form-item label="新权限标识" prop="new_permission">
          <el-input
            v-model="updateForm.new_permission"
            placeholder="如 document:read"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="updateDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleUpdate">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 批量设置权限弹窗 -->
    <el-dialog v-model="setDialogVisible" title="批量设置权限" width="480px" :close-on-click-modal="false">
      <p class="set-tip">
        <el-icon style="color: #e6a23c; vertical-align: -2px"><Warning /></el-icon>
        此操作将<b>覆盖</b>该用户现有的所有权限，每行输入一条权限标识。
      </p>
      <el-input
        v-model="setBatchText"
        type="textarea"
        :rows="8"
        placeholder="每行一条权限，如：&#10;document:read&#10;document:delete&#10;admin:view"
      />
      <template #footer>
        <el-button @click="setDialogVisible = false">取消</el-button>
        <el-button type="warning" :loading="submitting" @click="handleSet">确认覆盖设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus, Edit, Delete, Warning } from '@element-plus/icons-vue'
import request from '@/api/request'

// ── 状态 ──────────────────────────────────────────────
const searchUserName  = ref('')
const currentUserName = ref('')
const permissionList  = ref([])
const searching       = ref(false)
const tableLoading    = ref(false)
const submitting      = ref(false)

// 弹窗可见性
const addDialogVisible    = ref(false)
const updateDialogVisible = ref(false)
const setDialogVisible    = ref(false)

// 表单
const addFormRef    = ref(null)
const updateFormRef = ref(null)

const addForm = reactive({ permission: '' })
const updateForm = reactive({ permission: '', new_permission: '' })
const setBatchText = ref('')

// 表单校验规则
const addRules = {
  permission: [{ required: true, message: '请输入权限标识', trigger: 'blur' }]
}
const updateRules = {
  new_permission: [{ required: true, message: '请输入新权限标识', trigger: 'blur' }]
}

// ── 工具函数 ──────────────────────────────────────────
const callApi = (action, extra = {}) =>
  request.post('/system/user_permission', {
    action,
    user_name: currentUserName.value,
    ...extra
  })

const refreshList = async () => {
  tableLoading.value = true
  try {
    const res = await callApi('get')
    if (res.data?.code === 200) {
      permissionList.value = res.data.data || []
    } else {
      ElMessage.error(res.data?.msg || '获取权限失败')
    }
  } catch {
    ElMessage.error('网络请求失败')
  } finally {
    tableLoading.value = false
  }
}

// ── 查询 ─────────────────────────────────────────────
const handleSearch = async () => {
  const name = searchUserName.value.trim()
  if (!name) { ElMessage.warning('请输入用户名'); return }
  currentUserName.value = name
  await refreshList()
}

// ── 新增 ─────────────────────────────────────────────
const openAddDialog = () => {
  addForm.permission = ''
  addDialogVisible.value = true
}
const handleAdd = async () => {
  await addFormRef.value?.validate()
  submitting.value = true
  try {
    const res = await callApi('add', { permission: addForm.permission.trim() })
    if (res.data?.code === 200) {
      ElMessage.success('权限添加成功')
      addDialogVisible.value = false
      await refreshList()
    } else {
      ElMessage.error(res.data?.msg || '添加失败')
    }
  } catch {
    ElMessage.error('网络请求失败')
  } finally {
    submitting.value = false
  }
}

// ── 修改 ─────────────────────────────────────────────
const openUpdateDialog = (perm) => {
  updateForm.permission = perm
  updateForm.new_permission = ''
  updateDialogVisible.value = true
}
const handleUpdate = async () => {
  await updateFormRef.value?.validate()
  submitting.value = true
  try {
    const res = await callApi('update', {
      permission: updateForm.permission,
      new_permission: updateForm.new_permission.trim()
    })
    if (res.data?.code === 200) {
      ElMessage.success('权限修改成功')
      updateDialogVisible.value = false
      await refreshList()
    } else {
      ElMessage.error(res.data?.msg || '修改失败')
    }
  } catch {
    ElMessage.error('网络请求失败')
  } finally {
    submitting.value = false
  }
}

// ── 批量设置 ─────────────────────────────────────────
const openSetDialog = () => {
  setBatchText.value = permissionList.value.map(p => p.permission).join('\n')
  setDialogVisible.value = true
}
const handleSet = async () => {
  const perms = setBatchText.value
    .split('\n')
    .map(s => s.trim())
    .filter(Boolean)
  submitting.value = true
  try {
    const res = await callApi('set', { permissions: perms })
    if (res.data?.code === 200) {
      ElMessage.success('权限设置成功')
      setDialogVisible.value = false
      await refreshList()
    } else {
      ElMessage.error(res.data?.msg || '设置失败')
    }
  } catch {
    ElMessage.error('网络请求失败')
  } finally {
    submitting.value = false
  }
}

// ── 删除单条 ─────────────────────────────────────────
const handleDelete = async (perm) => {
  try {
    const res = await callApi('delete', { permission: perm })
    if (res.data?.code === 200) {
      ElMessage.success('权限删除成功')
      await refreshList()
    } else {
      ElMessage.error(res.data?.msg || '删除失败')
    }
  } catch {
    ElMessage.error('网络请求失败')
  }
}

// ── 清空所有权限 ──────────────────────────────────────
const handleDeleteAll = async () => {
  try {
    const res = await callApi('delete_all')
    if (res.data?.code === 200) {
      ElMessage.success('已清空该用户所有权限')
      await refreshList()
    } else {
      ElMessage.error(res.data?.msg || '清空失败')
    }
  } catch {
    ElMessage.error('网络请求失败')
  }
}
</script>

<style scoped>
.user-permission-container {
  padding: 10px 20px;
}

.search-bar {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
}

.user-section {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.user-label {
  font-size: 13px;
  color: #606266;
}

.header-actions {
  display: flex;
  gap: 6px;
}

.permission-table {
  width: 100%;
}

.set-tip {
  font-size: 13px;
  color: #606266;
  margin-bottom: 10px;
  line-height: 1.6;
}

:deep(.el-input__wrapper) {
  border-radius: 0;
}

:deep(.el-button) {
  border-radius: 0;
}

:deep(.el-table) {
  border-radius: 0;
}
</style>
