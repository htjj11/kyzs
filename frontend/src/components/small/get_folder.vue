<template>
  <el-dialog
    v-model="dialogVisible"
    title="选择文件夹"
    width="400px"
    center
    @close="handleClose"
  >
    <div class="folder-selector">
      <div v-if="loading" class="loading-container">
        <el-skeleton animated :rows="3" />
      </div>
      
      <el-tree
        v-else
        ref="treeRef"
        :data="folderTree"
        :props="defaultProps"
        @node-click="handleNodeClick"
        :default-expanded-keys="defaultExpandedKeys"
        node-key="id"
        highlight-current
      >
        <template #default="{ node }">
          <span class="custom-tree-node">
            <span>{{ node.label }}</span>
          </span>
        </template>
      </el-tree>
      
      <el-empty v-if="!loading && folderTree.length === 0" description="暂无文件夹数据" />
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :disabled="!selectedFolderId">
          确认选择
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import api from '@/api/request';

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  defaultFolderId: {
    type: [Number, String],
    default: null
  }
});

// Emits
const emit = defineEmits(['close', 'select-folder']);

// 响应式数据
const dialogVisible = ref(false);
const loading = ref(false);
const folders = ref([]);
const selectedFolderId = ref(null);
const treeRef = ref(null);
const defaultExpandedKeys = ref([]);

// 树形结构配置
const defaultProps = {
  children: 'children',
  label: 'folder_name'
};

// 构建树形结构
const folderTree = computed(() => {
  // 将扁平数据转换为树形结构
  const buildTree = (items, parentId = null) => {
    return items
      .filter(item => item.parent_id === parentId)
      .map(item => {
        const children = buildTree(items, item.id);
        return {
          ...item,
          children: children.length > 0 ? children : []
        };
      });
  };
  
  return buildTree(folders.value);
});

// 获取文件夹数据
const fetchFolders = async () => {
  loading.value = true;
  try {
    const response = await api({
      url: '/llm/get_all_folders',
      method: 'post',
      data: {}
    });
    
    if (response.data && response.data.code === 200) {
      folders.value = response.data.data || [];
      
      // 如果有默认选中的文件夹，设置选中状态
      if (props.defaultFolderId) {
        selectedFolderId.value = props.defaultFolderId;
        // 展开默认选中的文件夹路径
        expandNodePath(props.defaultFolderId);
      } else if (folders.value.length > 0) {
        // 默认选中第一个文件夹
        const firstFolder = folderTree.value[0];
        if (firstFolder) {
          selectedFolderId.value = firstFolder.id;
          defaultExpandedKeys.value = [firstFolder.id];
        }
      }
    } else {
      ElMessage.error(response.data?.msg || '获取文件夹列表失败');
    }
  } catch (error) {
    console.error('获取文件夹列表失败:', error);
    ElMessage.error('获取文件夹列表失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 展开节点路径
const expandNodePath = (nodeId) => {
  const findPath = (items, id, path = []) => {
    for (const item of items) {
      if (item.id === id) {
        return [...path, id];
      }
      if (item.children && item.children.length > 0) {
        const result = findPath(item.children, id, [...path, item.id]);
        if (result) {
          return result;
        }
      }
    }
    return null;
  };
  
  const path = findPath(folderTree.value, nodeId);
  if (path) {
    defaultExpandedKeys.value = path;
    // 延迟设置当前节点高亮，确保树已渲染
    setTimeout(() => {
      if (treeRef.value) {
        treeRef.value.setCurrentKey(nodeId);
      }
    }, 0);
  }
};

// 处理节点点击
const handleNodeClick = (data) => {
  selectedFolderId.value = data.id;
  
  // 立即获取选中的文件夹数据并返回给父组件
  const selectedFolder = folders.value.find(folder => folder.id === selectedFolderId.value);
  if (selectedFolder) {
    emit('confirm', {
      id: selectedFolder.id,
      name: selectedFolder.folder_name,
      fullPath: selectedFolder.full_path
    });
  } else {
    emit('confirm', {
      id: selectedFolderId.value
    });
  }
  
  // 关闭对话框
  dialogVisible.value = false;
  handleClose();
}

// 确认选择
const handleConfirm = () => {
  if (!selectedFolderId.value) {
    ElMessage.warning('请选择一个文件夹');
    return;
  }
  
  const selectedFolder = folders.value.find(folder => folder.id === selectedFolderId.value);
  if (selectedFolder) {
    emit('select-folder', {
      id: selectedFolder.id,
      name: selectedFolder.folder_name,
      fullPath: selectedFolder.full_path
    });
  } else {
    emit('select-folder', {
      id: selectedFolderId.value
    });
  }
  
  handleClose();
};

// 关闭对话框
const handleClose = () => {
  emit('close');
  // 重置选中状态，准备下次打开
  selectedFolderId.value = null;
  defaultExpandedKeys.value = [];
  if (treeRef.value) {
    treeRef.value.setCurrentKey(null);
  }
};

// 监听对话框显示状态
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal;
  if (newVal) {
    fetchFolders();
  }
});

// 监听默认文件夹ID变化
watch(() => props.defaultFolderId, (newVal) => {
  if (newVal && dialogVisible.value && !loading.value) {
    selectedFolderId.value = newVal;
    expandNodePath(newVal);
  }
});
</script>

<style scoped>
.folder-selector {
  max-height: 300px;
  overflow-y: auto;
}

.loading-container {
  padding: 20px;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 4px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 美化滚动条 */
.folder-selector::-webkit-scrollbar {
  width: 6px;
}

.folder-selector::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.folder-selector::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.folder-selector::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>