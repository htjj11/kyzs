<template>
    <div class="public-db-container">
        <div class="db-layout">
            <!-- 左侧分类树 -->
            <div class="db-sidebar">
                <div class="sidebar-header">
                    <h3 class="sidebar-title">知识库分类</h3>
                    <el-button link type="primary" @click="fetchStructure">
                        <el-icon>
                            <Refresh />
                        </el-icon>
                    </el-button>
                </div>
                <div class="sidebar-content">
                    <el-skeleton :loading="loadingStructure" animated>
                        <template #template>
                            <div style="padding: 14px">
                                <el-skeleton-item variant="p" style="width: 80%; margin-bottom: 12px" />
                                <el-skeleton-item variant="p" style="width: 60%; margin-bottom: 12px" />
                                <el-skeleton-item variant="p" style="width: 70%; margin-bottom: 12px" />
                            </div>
                        </template>
                        <template #default>
                            <el-tree ref="treeRef" class="category-tree" :data="categoryTree" :props="defaultProps"
                                highlight-current node-key="id" @node-click="handleNodeClick">
                                <template #default="{ node, data }">
                                    <span class="custom-tree-node">
                                        <span class="node-numbering">{{ data.numbering }}</span>
                                        <el-icon class="node-icon">
                                            <Folder v-if="!data.is_file" />
                                            <Document v-else />
                                        </el-icon>
                                        <span class="node-label">
                                            {{ node.label }}
                                            <span v-if="data.file_count !== undefined" class="node-count">
                                                ({{ data.file_count }})
                                            </span>
                                        </span>
                                    </span>
                                </template>
                            </el-tree>
                        </template>
                    </el-skeleton>
                </div>
            </div>

            <!-- 右侧文档列表 -->
            <div class="db-main">
                <div class="main-header">
                    <div class="breadcrumb-container">
                        <el-breadcrumb separator="/">
                            <el-breadcrumb-item>公共知识库</el-breadcrumb-item>
                            <el-breadcrumb-item v-if="selectedNode">
                                <span class="breadcrumb-numbering" v-if="selectedNode.numbering">{{
                                    selectedNode.numbering }}</span>
                                {{ selectedNode.name }}
                            </el-breadcrumb-item>
                        </el-breadcrumb>
                    </div>
                    <div class="header-actions">
                        <el-input v-model="searchQuery" placeholder="搜索文档并直接跳转..." class="search-input" clearable
                            @keydown="handleSearch">
                            <template #prefix>
                                <el-icon>
                                    <Search />
                                </el-icon>
                            </template>
                            <template #append>
                                <el-button @click="handleSearch">
                                    <el-icon>
                                        <Search />
                                    </el-icon>
                                </el-button>
                            </template>
                        </el-input>
                        <el-button type="primary" class="square-btn" :disabled="!selectedNode"
                            @click="showUploadModal = true">
                            <el-icon>
                                <Upload />
                            </el-icon> 上传文档
                        </el-button>
                    </div>
                </div>

                <div class="main-body">
                    <div v-if="!selectedNode" class="empty-state">
                        <el-empty description="请从左侧选择一个分类以查看文档" />
                    </div>
                    <div v-else class="table-container">
                        <el-table v-loading="loadingDocuments" :data="documentList" border stripe style="width: 100%"
                            class="scientific-table">
                            <el-table-column prop="id" label="ID" width="80" />
                            <el-table-column prop="title" label="文档标题" />
                            <el-table-column prop="file_type" label="类型" width="100" />
                            <el-table-column prop="file_size" label="大小" width="120">
                                <template #default="scope">
                                    {{ (scope.row.file_size / 1024).toFixed(2) }} KB
                                </template>
                            </el-table-column>
                            <el-table-column prop="created_at" label="上传时间" width="180" />
                            <el-table-column label="操作" width="150" align="center">
                                <template #default="scope">
                                    <el-button link type="primary" @click="viewDocument(scope.row)">查看</el-button>
                                    <el-button link type="danger" @click="deleteDocument(scope.row)">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </div>
            </div>
        </div>

        <!-- 上传弹窗 -->
        <el-dialog v-model="showUploadModal" title="批量上传文档" width="800px" append-to-body destroy-on-close>
            <public_db_upload v-if="selectedNode" :category-id="selectedNode.id" @success="handleUploadSuccess"
                @cancel="showUploadModal = false" />
        </el-dialog>

        <!-- 查看详情弹窗 -->
        <el-dialog v-model="showViewModal" title="文档详细信息" width="700px" append-to-body destroy-on-close>
            <public_db_view v-if="selectedFileId" :file-id="selectedFileId" @close="showViewModal = false" />
        </el-dialog>
        <!-- 搜索结果弹窗 -->
        <el-dialog v-model="showSearchModal" title="搜索结果" width="800px" top="10vh" class="scientific-dialog">
            <el-table :data="searchResults" border stripe max-height="400px">
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="title" label="文档标题" />
                <el-table-column label="操作" width="100" fixed="right">
                    <template #default="{ row }">
                        <el-button link type="primary" @click="viewDocument(row)">查看</el-button>
                    </template>
                </el-table-column>
            </el-table>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="showSearchModal = false" class="square-btn">关闭</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
    Refresh,
    Folder,
    Document,
    Search,
    Upload
} from '@element-plus/icons-vue'
import request from '@/api/request'
import public_db_upload from './public_db_upload.vue'
import public_db_view from './public_db_view.vue'

const loadingStructure = ref(false)
const loadingDocuments = ref(false)
const showUploadModal = ref(false)
const showViewModal = ref(false)
const categoryTree = ref([])
const treeRef = ref(null)
const selectedNode = ref(null)
const selectedFileId = ref(null)
const searchQuery = ref('')
const documentList = ref([])
const searchResults = ref([])
const showSearchModal = ref(false)

const defaultProps = {
    children: 'children',
    label: 'name',
}

// 获取知识库结构
const fetchStructure = async () => {
    loadingStructure.value = true
    try {
        const response = await request.post('/get_knowledge/get_structure')
        if (response.data && response.data.code === 200) {
            // 后端返回的是扁平数组，需要转换为树形结构并加上序号
            const flatList = response.data.data || []
            categoryTree.value = assembleTreeWithNumbering(flatList)
        } else {
            ElMessage.error('获取结果结构失败')
        }
    } catch (error) {
        console.error('获取结构错误:', error)
        ElMessage.error('获取结构失败，请检查网络连接')
    } finally {
        loadingStructure.value = false
    }
}

// 扁平数组转树型并递归增加序号
const assembleTreeWithNumbering = (list) => {
    const map = {}
    const roots = []

    // 1. 初始化映射
    list.forEach(item => {
        map[item.id] = { ...item, children: [] }
    })

    // 2. 建立父子关系
    list.forEach(item => {
        const node = map[item.id]
        if (item.parent_id && map[item.parent_id]) {
            map[item.parent_id].children.push(node)
        } else {
            roots.push(node)
        }
    })

    // 3. 递归分配序号
    const assignNumbering = (nodes, prefix = '') => {
        nodes.forEach((node, index) => {
            const currentNumbering = prefix ? `${prefix}.${index + 1}` : `${index + 1}`
            node.numbering = currentNumbering
            if (node.children && node.children.length > 0) {
                assignNumbering(node.children, currentNumbering)
            }
        })
    }

    assignNumbering(roots)
    return roots
}

// 递归查找并更新节点
const updateNodeData = (nodes, id, updates) => {
    for (const node of nodes) {
        if (node.id === id) {
            Object.assign(node, updates)
            return true
        }
        if (node.children && node.children.length > 0) {
            if (updateNodeData(node.children, id, updates)) return true
        }
    }
    return false
}
//处理点击某个分类，自动获取下级目录的数量
const handleNodeClick = async (data, node) => {
    selectedNode.value = data

    // 如果是具有子节点的文件夹
    if (data.children && data.children.length > 0) {
        // 只有在节点处于展开状态（包括即将展开）时检索子节点计数
        // 这里为了确保用户点击时能看到数据，我们在点击时就顺便刷新计数
        console.log(`正在更新目录 ${data.name} 的子项文档计数...`)

        const fetchCounts = data.children.map(async (child) => {
            if (child.file_count === undefined) {
                try {
                    const response = await request.post('/get_knowledge/get_files_by_category_id', {
                        category_id: child.id
                    })
                    if (response.data && response.data.code === 200) {
                        child.file_count = (response.data.data || []).length
                    }
                } catch (error) {
                    console.error(`获取分类 ${child.id} 计数失败:`, error)
                }
            }
        })

        await Promise.all(fetchCounts)
        // 依然需要这个通知，因为我们在自定义模板里用了 file_count
        // 而 Vue 3 的 el-tree 的 node 对象不一定会实时监听数据对象上的新属性
        // categoryTree.value = [...categoryTree.value]
    }

    // 调用获取当前分类文档列表
    fetchDocuments(data.id)
}

// 获取某个分类下的文档列表
const fetchDocuments = async (categoryId) => {
    if (!categoryId) return
    loadingDocuments.value = true
    try {
        const response = await request.post('/get_knowledge/get_files_by_category_id', { category_id: categoryId })
        if (response.data && response.data.code === 200) {
            documentList.value = response.data.data || []
        } else {
            ElMessage.error('获取文档列表失败')
        }
    } catch (error) {
        console.error('获取文档错误:', error)
        documentList.value = []
    } finally {
        loadingDocuments.value = false
    }
}

const handleUploadSuccess = () => {
    showUploadModal.value = false
    if (selectedNode.value) {
        fetchDocuments(selectedNode.value.id)
    }
}

const viewDocument = (row) => {
    selectedFileId.value = row.id
    showViewModal.value = true
}

const deleteDocument = (row) => {
    ElMessageBox.confirm('确定要删除该文档吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        ElMessage.success('删除成功')
    })
}

// 搜索功能实现
const handleSearch = async (event) => {
    // 如果是键盘事件且不是回车键，则退出
    if (event && event.type === 'keydown' && event.key !== 'Enter') return

    if (!searchQuery.value.trim()) {
        ElMessage.warning('请输入搜索关键字')
        return
    }

    loadingDocuments.value = true
    try {
        const response = await request.post('/get_knowledge/search_keyword', {
            keyword: searchQuery.value
        })

        if (response.data && response.data.code === 200 && response.data.data.length > 0) {
            searchResults.value = response.data.data
            showSearchModal.value = true
            ElMessage.success(`找到 ${searchResults.value.length} 条匹配结果`)
        } else {
            ElMessage.warning('未找到匹配的文档')
        }
    } catch (error) {
        console.error('搜索操作失败:', error)
        ElMessage.error('搜索请求失败')
    } finally {
        loadingDocuments.value = false
    }
}

onMounted(() => {
    fetchStructure()
})
</script>

<style scoped>
.public-db-container {
    height: 100%;
    padding: 16px;
    background-color: #f0f2f5;
    box-sizing: border-box;
}

.db-layout {
    display: flex;
    height: 100%;
    background: #fff;
    border: 1px solid #e4e7ed;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

/* 侧边栏样式 */
.db-sidebar {
    width: 450px;
    border-right: 1px solid #ebeef5;
    display: flex;
    flex-direction: column;
    background-color: #fafbfc;
    flex-shrink: 0;
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.sidebar-title {
    margin: 0;
    font-size: 15px;
    font-weight: 600;
    color: #303133;
}

.sidebar-content {
    flex: 1;
    overflow: auto;
    padding: 8px 0;
}

.category-tree {
    background: transparent;
    min-width: 100%;
    display: inline-block;
}

.custom-tree-node {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
}

.node-numbering {
    font-family: 'Courier New', Courier, monospace;
    font-size: 12px;
    color: #909399;
    min-width: 30px;
    display: inline-block;
}

.node-label {
    white-space: nowrap;
}

.node-count {
    color: #909399;
    font-size: 12px;
    margin-left: 4px;
    font-weight: normal;
}

.node-icon {
    font-size: 16px;
    color: #409eff;
}

/* 主内容样式 */
.db-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fff;
}

.breadcrumb-numbering {
    color: #909399;
    margin-right: 4px;
    font-weight: normal;
}

.main-header {
    padding: 16px 24px;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0;
}

.header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
}

.search-input {
    width: 240px;
}

.main-body {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.table-container {
    padding: 20px;
    flex: 1;
    overflow-y: auto;
}

/* 方正风格重置 */
.square-btn {
    border-radius: 0;
}

.scientific-table :deep(.el-table__inner-wrapper) {
    border-radius: 0;
}

:deep(.el-tree-node__content) {
    height: 36px;
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
    background-color: #ecf5ff;
    color: #409eff;
    border-right: 3px solid #409eff;
}

.empty-state {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
