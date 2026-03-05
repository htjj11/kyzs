<template>
  <div>
    <el-dialog
      v-model="dialogVisible"
      title="选择标签"
      width="30%"
      @open="handleOpen"
    >
      <div class="label-select-wrapper">
        <el-form label-width="80px">
          <el-form-item label="选择标签">
            <el-select v-model="selectedLabelId" placeholder="请选择标签">
              <el-option
                v-for="label in labelList"
                :key="label.id"
                :label="label.label_name"
                :value="label.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElDialog, ElSelect, ElOption, ElForm, ElFormItem, ElButton } from 'element-plus'
import { getUserIdFromCookie } from '@/utils/authUtils.js'
import request from '@/api/request.js'

// 定义组件props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

// 定义组件事件
const emit = defineEmits(['update:visible', 'selectLabel'])

// 组件状态
const dialogVisible = ref(false)
const labelList = ref([])
const selectedLabelId = ref(null)
const loading = ref(false)

// 监听visible属性变化，控制弹窗显示
watch(
  () => props.visible,
  (newVal) => {
    dialogVisible.value = newVal
  }
)

// 监听dialogVisible变化，同步到父组件
watch(
  dialogVisible,
  (newVal) => {
    emit('update:visible', newVal)
  }
)

// 获取标签列表
const fetchLabelList = async () => {
  try {
    loading.value = true
    // 从authUtils获取用户信息
    const userId = getUserIdFromCookie() || 1 // 默认使用1作为备用
    
    // 调用接口获取标签列表
    const response = await request.post('/get_setting/get_label', {
      user_id: userId
    })
    
    if (response.data.code === 200) {
      labelList.value = response.data.data || []
      // 默认选择第一个标签（如果有）
      if (labelList.value.length > 0 && !selectedLabelId.value) {
        selectedLabelId.value = labelList.value[0].id
      }
    } else {
      console.error('获取标签列表失败:', response.data.msg)
    }
  } catch (error) {
    console.error('请求标签列表出错:', error)
  } finally {
    loading.value = false
  }
}

// 弹窗打开时执行
const handleOpen = () => {
  // 重置选中状态
  selectedLabelId.value = null
  // 获取标签列表
  fetchLabelList()
}

// 确认选择
const handleConfirm = () => {
  if (selectedLabelId.value !== null) {
    // 将选中的标签ID传回父组件
    emit('selectLabel', {
      label_id: selectedLabelId.value
    })
    dialogVisible.value = false
  }
}

// 组件挂载时初始化
onMounted(() => {
  // 如果初始可见，则获取标签列表
  if (props.visible) {
    fetchLabelList()
  }
})
</script>

<style scoped>
.label-select-wrapper {
  padding: 10px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-select) {
  width: 100%;
}
</style>