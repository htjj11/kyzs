<template>
  <div class="all-db-container">
    <div class="content-wrapper">
      <!-- 左侧目录树 -->
      <div class="sidebar">
        <div class="sidebar-header">
          <h3>公共知识库目录</h3>
        </div>
        <div class="sidebar-content">
          <el-tree
            v-if="folderTree.length > 0"
            :data="folderTree"
            :props="defaultProps"
            @node-click="handleNodeClick"
            :default-expanded-keys="['public-root']"
            :default-checked-keys="[]"
            node-key="id"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span>{{ node.label }}</span>
                <span class="file-count" v-if="data.count > 0">({{ data.count }})</span>
              </span>
            </template>
          </el-tree>
          <div v-else class="loading-container">
            <el-skeleton animated />
          </div>
        </div>
      </div>

      <!-- 右侧内容列表 -->
      <div class="main-content">
        <div class="content-header">
          <h3>{{ currentPath || '所有内容' }}</h3>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索内容标题"
            prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </div>
        
        <div class="content-list">
          <div v-if="loading" class="loading">
            <el-skeleton animated :rows="5" />
          </div>
          <el-empty v-else-if="paginatedItems.length === 0" description="暂无数据" />
          <el-card
            v-else
            v-for="item in paginatedItems"
            :key="item.id"
            class="content-card"
          >
            <div class="card-header">
              <h4 class="content-title">{{ item.text_title }}</h4>
              <span class="publish-date">{{ formatDate(item.publish_date) }}</span>
            </div>
            <div class="card-footer">
              <el-button size="small" type="primary" @click="handleViewDetail(item)">
                查看详情
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 分页 -->
        <div v-if="filteredItems.length > 0" class="pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredItems.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
    
    <!-- 详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="文档详情"
      width="70%"
      @close="handleCloseDetail"
    >
      <div v-if="detailLoading" class="detail-loading">
        <el-skeleton animated :rows="10" />
      </div>
      <div v-else-if="detailData.id" class="detail-content">
        <div class="detail-header">
          <h2 class="detail-title">{{ detailData.text_title || '无标题' }}</h2>
          <div class="detail-meta">
            <span class="meta-item">ID: {{ detailData.id }}</span>
            <span class="meta-item">上传者: {{ detailData.username }}</span>
            <span class="meta-item">知识ID: {{ detailData.knowledge_id }}</span>
            <span class="meta-item">发布时间: {{ formatDate(detailData.publish_date) }}</span>
          </div>
        </div>
        
        <div class="detail-body">
          <h3 class="section-title">内容详情</h3>
          <div class="content-text">
            <pre>{{ detailData.text_content || '无内容' }}</pre>
          </div>
        </div>
        
        <div class="detail-footer">
          <h3 class="section-title">文档信息</h3>
          <div class="info-item">
            <strong>文本位置:</strong>
            <span>{{ detailData.text_location || '未知' }}</span>
          </div>
          <div class="info-item">
            <strong>文本ID:</strong>
            <span>{{ detailData.text_id || '未知' }}</span>
          </div>
          <div class="info-item">
            <strong>文件夹ID:</strong>
            <span>{{ detailData.folder_id || '未知' }}</span>
          </div>
        </div>
        
        <div class="detail-actions">
          <el-button 
            type="primary" 
            @click="handleAddToKnowledge" 
            :loading="addToKnowledgeLoading"
          >
            添加到个人知识库
          </el-button>
        </div>
      </div>
      <div v-else class="detail-empty">
        <el-empty description="暂无详情数据" />
      </div>
    </el-dialog>
    
    <!-- 标签选择对话框 -->
    <GetLabelList
      v-model:visible="showLabelDialog"
      @selectLabel="handleLabelSelected"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '@/api/request';
import GetLabelList from '../small/get_label_list.vue';
import { getUserIdFromCookie } from '@/utils/authUtils.js';

// 响应式数据
const loading = ref(false);
const allData = ref([]);
const searchKeyword = ref('');
const currentPath = ref('公共知识库');
const currentFolder = ref('公共知识库');
// 详情相关数据
const showDetailDialog = ref(false);
const detailLoading = ref(false);
const detailData = ref({});
// 标签选择相关
const showLabelDialog = ref(false);
const addToKnowledgeLoading = ref(false);

// 分页相关
const currentPage = ref(1);
const pageSize = ref(10);

// 树形结构配置
const defaultProps = {
  children: 'children',
  label: 'label'
};

// 文件夹树数据
const folderTree = computed(() => {
  // 创建目录映射，用于快速查找和构建目录树
  const folderMap = new Map();
  
  // 创建根节点
  const rootNode = {
    id: 'public-root',
    label: '公共知识库',
    path: '公共知识库',
    count: 0,
    children: []
  };
  folderMap.set('公共知识库', rootNode);

  // 处理所有文件，构建目录树结构
  allData.value.forEach(item => {
    const folderPath = item.folder_path;
    
    // 为根目录下的文件计数
    if (folderPath === '公共知识库') {
      rootNode.count++;
      return;
    }
    
    // 处理有层级的目录
    if (folderPath.includes('/')) {
      const parts = folderPath.split('/');
      let currentPath = '';
      
      // 递归创建每个层级的目录节点
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        currentPath = i === 0 ? part : `${currentPath}/${part}`;
        
        // 如果该目录节点不存在，创建它
        if (!folderMap.has(currentPath)) {
          const newNode = {
            id: currentPath,
            label: part,
            path: currentPath,
            count: 0,
            children: []
          };
          folderMap.set(currentPath, newNode);
          
          // 如果不是根节点，将其添加到父节点的children中
          if (i > 0) {
            const parentPath = parts.slice(0, i).join('/');
            const parentNode = folderMap.get(parentPath);
            if (parentNode) {
              parentNode.children.push(newNode);
            }
          }
        }
      }
      
      // 为最深层的目录计数（文件所在的目录）
      const leafNode = folderMap.get(folderPath);
      if (leafNode) {
        leafNode.count++;
      }
    }
  });

  return [rootNode];
});

// 过滤后的当前文件夹内容
const currentFolderItems = computed(() => {
  return allData.value.filter(item => {
    return item.folder_path === currentFolder.value;
  });
});

// 搜索过滤后的内容
const filteredItems = computed(() => {
  if (!searchKeyword.value.trim()) {
    return currentFolderItems.value;
  }
  const keyword = searchKeyword.value.toLowerCase().trim();
  return currentFolderItems.value.filter(item => 
    item.text_title.toLowerCase().includes(keyword)
  );
});

// 分页后的数据
const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredItems.value.slice(start, end);
});



// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    const response = await api({
      url: '/llm/get_public_anything_db',
      method: 'post',
      data: {}
    });
    
    if (response.data.code === 200) {
      allData.value = response.data.data || [];
    } else {
      ElMessage.error(response.msg || '获取数据失败');
    }
  } catch (error) {
    console.error('获取公共知识库数据失败:', error);
    ElMessage.error('获取数据失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 处理节点点击
const handleNodeClick = (data) => {
  currentPath.value = data.path;
  currentFolder.value = data.path;
  currentPage.value = 1; // 切换目录时重置页码
};

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1; // 搜索时重置页码
};

// 处理分页大小变化
const handleSizeChange = (size) => {
  pageSize.value = size;
  currentPage.value = 1;
};

// 处理当前页码变化
const handleCurrentChange = (current) => {
  currentPage.value = current;
};

// 查看详情
const handleViewDetail = async (item) => {
  showDetailDialog.value = true;
  detailLoading.value = true;
  
  try {
    const response = await api({
      url: '/llm/get_anything_db_by_id',
      method: 'post',
      data: { id: item.id }
    });
    
    if (response.data.code === 200) {
      detailData.value = response.data.data || {};
    } else {
      ElMessage.error(response.data.msg || '获取详情失败');
      detailData.value = {};
    }
  } catch (error) {
    console.error('获取详情失败:', error);
    ElMessage.error('获取详情失败，请重试');
    detailData.value = {};
  } finally {
    detailLoading.value = false;
  }
};

// 关闭详情对话框
const handleCloseDetail = () => {
  showDetailDialog.value = false;
  detailData.value = {};
};

// 处理添加到个人知识库
const handleAddToKnowledge = () => {
  // 显示标签选择对话框
  showLabelDialog.value = true;
};

// 处理标签选择结果
const handleLabelSelected = async (result) => {
  if (!result || !result.label_id) return;
  
  addToKnowledgeLoading.value = true;
  
  try {
    // 准备数据
    const dataDict = {
      title_string: detailData.value.text_title || '无标题',
      content_string: detailData.value.text_content || '',
      source_id: detailData.value.id,
      source_type: 'database'
    };
    
    // 调用添加收藏接口
    const response = await api({
      url: '/add_to_knowledge/add_knowledge',
      method: 'post',
      data: {
        data_dict: dataDict,
        label_id: result.label_id,
        type_id: 4 // 自定义信息类型
      }
    });
    
    if (response.data.code === 200) {
      ElMessage.success('添加到个人知识库成功');
    } else {
      ElMessage.error(response.data.msg || '添加失败，请重试');
    }
  } catch (error) {
    console.error('添加到知识库失败:', error);
    ElMessage.error('添加失败，请重试');
  } finally {
    addToKnowledgeLoading.value = false;
  }
};

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '未知';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch (error) {
    return dateString;
  }
};

// 组件挂载时获取数据
onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.all-db-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background-color: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #fff;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.content-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.content-header .el-input {
  width: 300px;
}

.content-list {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}

.content-card {
  margin-bottom: 15px;
  transition: all 0.3s;
}

.content-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.content-title {
  margin: 0;
  font-size: 16px;
  color: #303133;
  flex: 1;
  margin-right: 15px;
}

.publish-date {
  font-size: 14px;
  color: #909399;
  white-space: nowrap;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.loading-container {
  padding: 20px;
}

.loading {
  padding: 20px;
}

.detail-loading {
  padding: 20px 0;
}

.detail-content {
  padding: 10px 0;
}

.detail-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  color: #303133;
  line-height: 1.4;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.meta-item {
  font-size: 14px;
  color: #909399;
  background-color: #f5f7fa;
  padding: 4px 12px;
  border-radius: 4px;
}

.detail-body,
.detail-footer {
  margin-bottom: 24px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #606266;
}

.content-text {
  background-color: #fafafa;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  max-height: 400px;
  overflow-y: auto;
}

.content-text pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-item strong {
  min-width: 80px;
  color: #606266;
}

.info-item span {
  color: #303133;
  word-break: break-all;
}

.detail-empty {
  padding: 40px 0;
}

.detail-actions {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  width: 100%;
}

.file-count {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-wrapper {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .content-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .content-header .el-input {
    width: 100%;
    margin-top: 10px;
  }
}
</style>