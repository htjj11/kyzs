<template>
  <div class="db-manage-container">
    <div class="db-manage-header">
      <h2>大模型知识库管理（仅展示当前用户的知识）</h2>
      <el-button 
        type="primary" 
        @click="fetchKnowledgeList"
        :loading="loading"
        icon="Refresh"
      >
        刷新数据
      </el-button>
    </div>
    
    <div class="db-manage-content">
      <!-- 数据列表 -->
      <el-table 
        v-loading="loading" 
        :data="knowledgeList" 
        style="width: 100%"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />

        <el-table-column prop="text_title" label="标题" min-width="200">
          <template #default="scope">
            <el-popover 
              placement="top" 
              width="400" 
              trigger="hover"
            >
              <template #reference>
                <span class="title-text">{{ scope.row.text_title }}</span>
              </template>
              <div class="title-popover">
                {{ scope.row.text_title }}
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="publish_date" label="发布日期" width="180" align="center" />
        <el-table-column prop="full_full_path" label="存储路径" min-width="150" />
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="scope">
            <el-button 
              type="danger" 
              text 
              size="small"
              @click="handleDelete(scope.row)"
              :loading="deletingIds.includes(scope.row.id)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 空状态 -->
      <div v-if="!loading && knowledgeList.length === 0" class="empty-state">
        <el-empty description="暂无知识库数据" />
      </div>
      
      <!-- 分页 -->
      <div v-if="knowledgeList.length > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api/request'

// 数据加载状态
const loading = ref(false)
// 知识库列表数据
const knowledgeList = ref([])
// 删除中的ID列表，用于防止重复点击
const deletingIds = ref([])
// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取知识库列表
const fetchKnowledgeList = async () => {
  try {
    loading.value = true
    const response = await api.post('/llm/get_all_anything_db', {})
    
    if (response.data && response.data.code === 200 && response.data.msg === 'success') {
      knowledgeList.value = response.data.data || []
      console.log('获取到的anythingdb知识库数据:', knowledgeList.value)
      total.value = knowledgeList.value.length
    } else {
      ElMessage.error('获取知识库数据失败：' + (response.data?.msg || '未知错误'))
    }
  } catch (error) {
    console.error('获取知识库数据失败:', error)
    ElMessage.error('获取知识库数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理删除操作
const handleDelete = async (row) => {
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      '确定要从公共知识库中删除这条数据吗？此操作不可撤销。',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }
    )
    
    // 添加到删除中列表，防止重复点击
    deletingIds.value.push(row.id)
    
    // 调用删除接口
    const response = await api.post('/llm/delete_anything_db', {
      id: row.id
    })
    
    if (response.data && response.data.code === 200 && response.data.msg === 'success') {
      ElMessage.success('删除成功')
      // 重新获取数据列表
      await fetchKnowledgeList()
    } else {
      ElMessage.error('删除失败：' + (response.data?.msg || '未知错误'))
    }
  } catch (error) {
    // 如果用户取消，不显示错误信息
    if (error !== 'cancel') {
      console.error('删除知识库数据失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  } finally {
    // 从删除中列表移除
    deletingIds.value = deletingIds.value.filter(id => id !== row.id)
  }
}

// 分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  // 由于数据较少，这里不重新请求，只更新分页状态
}

// 当前页变化
const handleCurrentChange = (current) => {
  currentPage.value = current
  // 由于数据较少，这里不重新请求，只更新分页状态
}

// 组件挂载时获取数据
onMounted(() => {
  fetchKnowledgeList()
})
</script>

<style scoped>
.db-manage-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
}

.db-manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.db-manage-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.db-manage-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.title-text {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.title-popover {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>