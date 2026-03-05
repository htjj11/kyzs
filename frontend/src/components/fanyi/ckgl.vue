<template>
  <div class="word-library-container">
    <div class="header">
      <h2>翻译词库</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon>
          添加词汇
        </el-button>
        <el-button @click="exportWords">
          <el-icon><Download /></el-icon>
          导出词库
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="search-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchWord"
            placeholder="输入关键字模糊匹配"
            clearable
            @input="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="selectedType" placeholder="翻译类型" clearable @change="handleSearch">
            <el-option label="中英翻译" value="en" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="selectedField" placeholder="领域分类" clearable @change="handleSearch">
            <el-option label="石油工程" value="1" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="lookupWord">
            <el-icon><Search /></el-icon>
            查词
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 词汇表格 -->
    <div class="table-section">
      <el-table 
        :data="wordList" 
        stripe 
        border 
        style="width: 100%"
        :loading="loading"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="ts_type" label="翻译类型" width="120" />
        <el-table-column prop="field_id" label="领域" width="100">
          <template #default="{ row }">
            {{ getFieldName(row.field_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="content1" label="词汇" min-width="150" />
        <el-table-column prop="content2" label="释义" min-width="200" show-overflow-tooltip />
        <el-table-column prop="content3" label="用法说明" min-width="250" show-overflow-tooltip />
        <el-table-column prop="from" label="来源" width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editWord(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteWord(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-section">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalCount"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEdit ? '编辑词汇' : '添加词汇'"
      width="800px"
      @close="resetForm"
    >
      <el-form
        ref="wordFormRef"
        :model="wordForm"
        :rules="wordRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="翻译类型" prop="ts_type">
              <el-select v-model="wordForm.ts_type" placeholder="选择翻译类型">
                <el-option label="中英翻译" value="en" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="领域分类" prop="field_id">
              <el-select v-model="wordForm.field_id" placeholder="选择领域">
                <el-option label="石油工程" :value="1" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="词汇内容" prop="content1">
          <el-input 
            v-model="wordForm.content1" 
            placeholder="请输入词汇（通常为英文）"
            @blur="autoLookup"
          />
        </el-form-item>
        
        <el-form-item label="词汇释义" prop="content2">
          <el-input 
            v-model="wordForm.content2" 
            type="textarea" 
            :rows="3"
            placeholder="请输入词汇释义（通常为中文）"
          />
        </el-form-item>
        
        <el-form-item label="用法说明" prop="content3">
          <el-input 
            v-model="wordForm.content3" 
            type="textarea" 
            :rows="4"
            placeholder="请输入用法说明、注释等"
          />
        </el-form-item>
        
        <el-form-item label="词汇来源" prop="from">
          <el-input 
            v-model="wordForm.from" 
            placeholder="请输入该词汇的来源"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="saveWord">
            {{ isEdit ? '更新' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Search, 
  Download, 
  Edit, 
  Delete 
} from '@element-plus/icons-vue'
import request from '@/api/request'

// 响应式数据
const searchWord = ref('')
const selectedType = ref('')
const selectedField = ref('')
const loading = ref(false)
const wordList = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

const showAddDialog = ref(false)
const isEdit = ref(false)
const wordFormRef = ref()

// 词汇表单数据
const wordForm = reactive({
  id: null,
  ts_type: '',
  field_id: null,
  content1: '',
  content2: '',
  content3: '',
  from: ''
})

// 表单验证规则
const wordRules = {
  ts_type: [
    { required: true, message: '请选择翻译类型', trigger: 'change' }
  ],
  field_id: [
    { required: true, message: '请选择领域分类', trigger: 'change' }
  ],
  content1: [
    { required: true, message: '请输入词汇内容', trigger: 'blur' }
  ],
  content2: [
    { required: true, message: '请输入词汇释义', trigger: 'blur' }
  ]
}

// 领域名称映射
const fieldNames = {
  1: '石油工程'
}

// 获取领域名称
const getFieldName = (fieldId) => {
  return fieldNames[fieldId] || '未知'
}

// 保存所有搜索结果用于客户端分页
const allSearchResults = ref([])

// 搜索词汇
const handleSearch = async () => {
  currentPage.value = 1 // 重置到第一页
  await fetchWordList(true) // 传递true表示是搜索操作
}

// 获取词汇列表
const fetchWordList = async (isSearch = false) => {
  loading.value = true
  try {
    // 如果是搜索操作，获取完整结果
    if (isSearch) {
      const params = {
        content1: searchWord.value.trim(),
        ts_type: selectedType.value,
        field_id: selectedField.value
      }
      
      // 移除空值参数
      const cleanParams = {}
      Object.keys(params).forEach(key => {
        if (params[key] !== '' && params[key] !== null && params[key] !== undefined) {
          cleanParams[key] = params[key]
        }
      })
      
      // 调用获取词汇列表接口，不分页获取所有数据
      const response = await request.post('/translate/get_translate_word_list', cleanParams)
      
      if (response.data.code === 200) {
        allSearchResults.value = response.data.data.list || []
        totalCount.value = response.data.data.total || 0
      } else {
        ElMessage.error(response.data.msg || '搜索失败')
        allSearchResults.value = []
        totalCount.value = 0
      }
    }
    
    // 客户端分页显示当前页数据
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    wordList.value = allSearchResults.value.slice(start, end)
    
  } catch (error) {
    if (isSearch) {
      ElMessage.error('搜索失败')
      console.error('Search error:', error)
      allSearchResults.value = []
      totalCount.value = 0
    }
    wordList.value = []
  } finally {
    loading.value = false
  }
}

 
// 查词功能 - 使用统一的搜索逻辑
const lookupWord = async () => {
  if (!searchWord.value.trim()) {
    ElMessage.warning('请输入要查询的词汇')
    return
  }

  loading.value = true
  try {
    // 调用查词接口
    const response = await request.post('/translate/get_translate_word_by_content', {
      content1: searchWord.value.trim()
    })
    
    console.log('查词词典接口返回数据:', response.data)
    if (response.data['code'] === 200) {
        const data = response.data['data']
        console.log('查词词典接口返回数据:', data)
      if (data && data.length > 0) {
        // 保存搜索结果到allSearchResults，使用统一的分页逻辑
        allSearchResults.value = data
        totalCount.value = data.length
        currentPage.value = 1 // 重置到第一页
        
        // 客户端分页显示第一页数据
        const start = (currentPage.value - 1) * pageSize.value
        const end = start + pageSize.value
        wordList.value = allSearchResults.value.slice(start, end)
        
        ElMessage.success(`找到 ${data.length} 个相关词汇`)
      } else {
        // 未找到结果，清空数据
        allSearchResults.value = []
        wordList.value = []
        totalCount.value = 0
        ElMessage.info('未找到匹配的词汇，可以添加新词汇')
        showAddDialog.value = true
        wordForm.content1 = searchWord.value.trim()
      }
    } else {
      // 接口返回错误，清空数据
      allSearchResults.value = []
      wordList.value = []
      totalCount.value = 0
      ElMessage.warning(response.data.msg || '未找到匹配的词汇')
      showAddDialog.value = true
      wordForm.content1 = searchWord.value.trim()
    }
  } catch (error) {
    ElMessage.error('查词失败，请检查网络连接')
    console.error('Lookup error:', error)
    // 发生错误时清空数据
    allSearchResults.value = []
    wordList.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

// 自动查词
const autoLookup = () => {
  if (wordForm.content1 && !isEdit.value) {
    // 延迟500ms执行，避免频繁请求
    setTimeout(() => {
      lookupWord()
    }, 500)
  }
}

// 编辑词汇
const editWord = (row) => {
  isEdit.value = true
  Object.assign(wordForm, row)
  showAddDialog.value = true
}

// 删除词汇
const deleteWord = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除词汇 "${row.content1}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用删除词汇接口
    const response = await request.post('/translate/delete_translate_word', {
      word_id: row.id
    })
    
    if (response.data.code === 200) {
      ElMessage.success('删除成功')
    } else {
      ElMessage.error(response.data.msg || '删除失败')
      return
    }
    fetchWordList()
  } catch {
    // 用户取消删除
  }
}

// 保存词汇
const saveWord = async () => {
  if (!wordFormRef.value) return
  
  try {
    await wordFormRef.value.validate()
    
    if (isEdit.value) {
      // 更新词汇 - 调用更新词汇接口
      const updateData = {
        word_id: wordForm.id,
        ts_type: wordForm.ts_type,
        field_id: wordForm.field_id,
        content1: wordForm.content1,
        content2: wordForm.content2,
        content3: wordForm.content3,
        from_source: wordForm.from  // 注意：后端接口使用from_source参数
      }
      
      const response = await request.post('/translate/update_translate_word', updateData)
      
      if (response.data.code === 200) {
        ElMessage.success('词汇更新成功')
      } else {
        ElMessage.error(response.data.msg || '更新失败')
        return
      }
    } else {
      // 添加新词汇 - 调用增加单词接口
      const addData = {
        ts_type: wordForm.ts_type,
        field_id: wordForm.field_id,
        content1: wordForm.content1,
        content2: wordForm.content2,
        content3: wordForm.content3,
        from_source: wordForm.from  // 注意：后端接口使用from_source参数
      }
      
      const response = await request.post('/translate/add_translate_word', addData)
      
      if (response.data.code === 200) {
        ElMessage.success('词汇添加成功')
      } else {
        ElMessage.error(response.data.msg || '添加失败')
        return
      }
    }
    
    showAddDialog.value = false
    resetForm()
    // 如果当前有搜索结果，重新搜索以更新数据
    if (allSearchResults.value.length > 0) {
      await handleSearch()
    } else {
      // 否则清空显示
      wordList.value = []
      totalCount.value = 0
    }
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存失败，请检查输入信息')
    }
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(wordForm, {
    id: null,
    ts_type: '',
    field_id: null,
    content1: '',
    content2: '',
    content3: '',
    from: ''
  })
  isEdit.value = false
  wordFormRef.value?.clearValidate()
}

// 导出词库
const exportWords = () => {
  // 实现词库导出功能
  ElMessage.info('导出功能开发中...')
}

// 分页处理 - 仅客户端分页，不重新搜索
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1 // 重置到第一页
  // 客户端分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  wordList.value = allSearchResults.value.slice(start, end)
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  // 客户端分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  wordList.value = allSearchResults.value.slice(start, end)
}

// 初始化
onMounted(() => {
  // 初始化时不自动搜索，等待用户手动搜索
  // fetchWordList()
})
</script>

<style scoped>
.word-library-container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header h2 {
  margin: 0;
  color: #303133;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.pagination-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table th) {
  background-color: #fafafa;
  color: #606266;
  font-weight: 600;
}

/* 对话框样式 */
:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .word-library-container {
    padding: 10px;
  }
  
  .header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .search-section .el-row {
    flex-direction: column;
  }
  
  .search-section .el-col {
    margin-bottom: 16px;
  }
}
</style>