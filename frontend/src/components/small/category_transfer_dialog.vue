<template>
  <el-dialog v-model="dialogVisible" title="选择上传的公共知识库目标分类" width="450px" @open="handleOpen" append-to-body>
    <div v-loading="loadingStructure" style="height: 350px; overflow-y: auto;">
      <el-tree ref="treeRef" :data="categoryTree" :props="defaultProps" highlight-current node-key="id"
        @node-click="handleTransferNodeClick">
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span class="node-numbering" v-if="data.numbering"
              style="margin-right: 8px; font-family: Courier New; color: #909399;">{{ data.numbering }}</span>
            <el-icon class="node-icon" style="margin-right: 8px; color: #409eff;">
              <Folder v-if="!data.is_file" />
              <Document v-else />
            </el-icon>
            <span>{{ node.label }}</span>
          </span>
        </template>
      </el-tree>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedTransferNode || selectedTransferNode.is_file" @click="onConfirm">
          确定上传
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Folder, Document } from '@element-plus/icons-vue'
import api from '@/api/request'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:visible', 'confirm'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const loadingStructure = ref(false)
const categoryTree = ref([])
const selectedTransferNode = ref(null)

const defaultProps = {
  children: 'children',
  label: 'name',
}

// 格式化序号
const formatNumbering = (nodes, prefix = '') => {
  nodes.forEach((node, index) => {
    const currentNumbering = prefix ? `${prefix}.${index + 1}` : `${index + 1}`
    node.numbering = currentNumbering
    if (node.children && node.children.length > 0) {
      formatNumbering(node.children, currentNumbering)
    }
  })
}

// 建立树形
const buildTree = (list) => {
  const map = {}
  const roots = []
  list.forEach(item => { map[item.id] = { ...item, children: [] } })
  list.forEach(item => {
    if (item.parent_id && map[item.parent_id]) {
      map[item.parent_id].children.push(map[item.id])
    } else {
      roots.push(map[item.id])
    }
  })
  formatNumbering(roots)
  return roots
}

// 弹窗打开时加载数据
const handleOpen = async () => {
  selectedTransferNode.value = null
  loadingStructure.value = true
  try {
    const response = await api.post('/public_knowledgebase/get_structure')
    if (response.data && response.data.code === 200) {
      categoryTree.value = buildTree(response.data.data || [])
    } else {
      ElMessage.error('获取结果结构失败')
    }
  } catch (error) {
    console.error('获取结构错误:', error)
    ElMessage.error('获取结构失败')
  } finally {
    loadingStructure.value = false
  }
}

// 节点点击
const handleTransferNodeClick = (data) => {
  selectedTransferNode.value = data
}

// 确定点击
const onConfirm = () => {
  if (selectedTransferNode.value) {
    emit('confirm', selectedTransferNode.value)
  }
}
</script>

<style scoped>
.custom-tree-node {
  display: flex;
  align-items: center;
}
</style>
