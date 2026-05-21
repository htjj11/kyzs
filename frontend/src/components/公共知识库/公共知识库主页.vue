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
                        <el-button type="success" class="square-btn" @click="showChatModal = true">
                            <el-icon>
                                <ChatDotRound />
                            </el-icon> 知识库对话
                        </el-button>
                        <el-tooltip v-if="!hasUploadPermission" content="您没有权限上传公共知识库文件" placement="top">
                            <span style="display: inline-block; cursor: not-allowed;">
                                <el-button type="primary" class="square-btn" disabled style="pointer-events: none;">
                                    <el-icon>
                                        <Upload />
                                    </el-icon> 上传文档
                                </el-button>
                            </span>
                        </el-tooltip>
                        <el-button v-else type="primary" class="square-btn" :disabled="!selectedNode"
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
                                    <el-tooltip v-if="!hasDeletePermission" content="您没有删除公共知识库权限" placement="top">
                                        <span style="display: inline-block; cursor: not-allowed; margin-left: 12px;">
                                            <el-button link type="danger" disabled
                                                style="pointer-events: none;">删除</el-button>
                                        </span>
                                    </el-tooltip>
                                    <el-button v-else link type="danger" @click="deleteDocument(scope.row)"
                                        style="margin-left: 12px;">删除</el-button>
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

        <!-- 对话弹窗 -->
        <el-dialog v-model="showChatModal" title="知识库智能对话" width="80%" top="5vh" append-to-body destroy-on-close
            class="scientific-dialog">
            <public_db_chat />
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPermissionCookie, getUserIdFromCookie } from '@/utils/authUtils'
import {
    Refresh,
    Folder,
    Document,
    Search,
    Upload,
    ChatDotRound
} from '@element-plus/icons-vue'
import request from '@/api/request'
import public_db_upload from './公共知识库上传.vue'
import public_db_view from './公共知识库查看.vue'
import public_db_chat from './公共知识库对话.vue'

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
const showChatModal = ref(false)

const hasDeletePermission = computed(() => {
    const permissions = getPermissionCookie() || []
    return Array.isArray(permissions) ? permissions.includes('public_db_document:delete') : false
})

const hasUploadPermission = computed(() => {
    const permissions = getPermissionCookie() || []
    return Array.isArray(permissions) ? permissions.includes('public_db_document:upload') : false
})

const defaultProps = {
    children: 'children',
    label: 'name',
}

// 获取知识库结构
const fetchStructure = async () => {
    loadingStructure.value = true
    try {
        const response = await request.post('/public_knowledgebase/get_structure', {})
        if (response.data && response.data.code === 200) {
            const flatList = response.data.data || []
            categoryTree.value = assembleTreeWithNumbering(flatList)
            // 建树后立即并发拉取所有叶节点的文件数，再向上累加
            await loadAllFileCounts(categoryTree.value)
            // 触发响应式更新，让树重新渲染计数
            categoryTree.value = [...categoryTree.value]
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

// 一次性加载所有叶节点的文件数，并递归向上累加父节点的总和
const loadAllFileCounts = async (nodes) => {
    // 1. 收集所有叶节点
    const leaves = []
    const collectLeaves = (nodeList) => {
        nodeList.forEach(node => {
            if (!node.children || node.children.length === 0) {
                leaves.push(node)
            } else {
                collectLeaves(node.children)
            }
        })
    }
    collectLeaves(nodes)

    // 2. 并发请求所有叶节点的文件数
    await Promise.all(leaves.map(async (leaf) => {
        try {
            const res = await request.post('/public_knowledgebase/get_files_by_category_id', {
                category_id: leaf.id
            })
            if (res.data && res.data.code === 200) {
                leaf.file_count = (res.data.data || []).length
            } else {
                leaf.file_count = 0
            }
        } catch {
            leaf.file_count = 0
        }
    }))

    // 3. 自底向上递归累加：返回该子树的文件总数
    const sumCounts = (nodeList) => {
        nodeList.forEach(node => {
            if (node.children && node.children.length > 0) {
                sumCounts(node.children)
                node.file_count = node.children.reduce((acc, child) => acc + (child.file_count || 0), 0)
            }
            // 叶节点 file_count 已在上面赋值
        })
    }
    sumCounts(nodes)
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
// 点击节点：仅选中并加载文档（计数已在页面加载时完成）
const handleNodeClick = (data) => {
    selectedNode.value = data
    fetchDocuments(data.id)
}

// 获取某个分类下的文档列表
const fetchDocuments = async (categoryId) => {
    if (!categoryId) return
    loadingDocuments.value = true
    try {
        const response = await request.post('/public_knowledgebase/get_files_by_category_id', { category_id: categoryId })
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
    }).then(async () => {
        try {
            const response = await request.post('/public_knowledgebase/delete_public_file_by_id', {
                file_id: row.id,
                user_id: getUserIdFromCookie()
            })
            if (response.data && response.data.code === 200) {
                ElMessage.success('删除成功')
                // 刷新文档列表
                if (selectedNode.value) {
                    fetchDocuments(selectedNode.value.id)
                }
            } else {
                ElMessage.error('删除失败：' + (response.data?.msg || '未知错误'))
            }
        } catch (error) {
            console.error('删除文档错误:', error)
            ElMessage.error('删除文档失败')
        }
    }).catch(() => {
        // 取消删除
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
        const response = await request.post('/public_knowledgebase/search_keyword', {
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
    width: 350px;
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
