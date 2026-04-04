<template>
    <div class="upload-component">
        <el-upload class="upload-area" drag action="#" multiple :auto-upload="false" :on-change="handleFileChange"
            :on-remove="handleFileRemove" :file-list="fileList">
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
                <div class="el-upload__tip">
                    支持多文件上传，单个文件不超过 50MB
                </div>
            </template>
        </el-upload>

        <!-- 待上传文件列表（带详情编辑） -->
        <div v-if="uploadItems.length > 0" class="upload-list-container">
            <h4 class="list-title">待上传列表 ({{ uploadItems.length }})</h4>
            <div class="upload-items">
                <div v-for="(item, index) in uploadItems" :key="item.file.uid" class="upload-item-card">
                    <div class="item-main">
                        <div class="item-info">
                            <el-input v-model="item.title" placeholder="文档标题" class="item-title-input">
                                <template #prepend>标题</template>
                            </el-input>
                            <el-input v-model="item.description" type="textarea" :rows="1" placeholder="基本描述 (可选)"
                                class="item-desc-input" />
                            <el-select v-model="item.tags" multiple filterable allow-create default-first-option
                                placeholder="输入标签并回车" class="item-tags-select">
                                <el-option v-for="tag in commonTags" :key="tag" :label="tag" :value="tag" />
                            </el-select>
                        </div>
                        <div class="item-status">
                            <el-tag v-if="item.status === 'ready'" type="info">已就绪</el-tag>
                            <el-tag v-else-if="item.status === 'uploading'" type="warning">上传中...</el-tag>
                            <el-tag v-else-if="item.status === 'success'" type="success">成功</el-tag>
                            <el-tag v-else-if="item.status === 'skipped'" type="info">已跳过（相同文件）</el-tag>
                            <el-tag v-else-if="item.status === 'error'" type="danger">失败</el-tag>
                            <el-button v-if="item.status === 'ready' || item.status === 'error'" link type="danger"
                                @click="removeUploadItem(index)">
                                移除
                            </el-button>
                        </div>
                    </div>
                    <el-progress v-if="item.status === 'uploading'" :percentage="item.progress" :show-text="false"
                        class="item-progress" />
                </div>
            </div>
        </div>

        <div class="upload-actions">
            <el-button @click="$emit('cancel')">取消</el-button>
            <el-button type="primary" class="square-btn" :loading="isUploading" :disabled="uploadItems.length === 0"
                @click="startUpload">
                开始上传 ({{ uploadItems.length }}个文件)
            </el-button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import request from '@/api/request'

const props = defineProps({
    categoryId: {
        type: [Number, String],
        required: true
    }
})

const emit = defineEmits(['success', 'cancel'])

const fileList = ref([])
const uploadItems = ref([])
const isUploading = ref(false)
const commonTags = ref(['科学', '工程', '专利', '论文', '技术文档'])

// 监听文件选择
const handleFileChange = (file, list) => {
    fileList.value = list
    // 只添加新增的文件
    const exists = uploadItems.value.some(item => item.file.uid === file.uid)
    if (!exists) {
        uploadItems.value.push({
            file: file,
            title: file.name.substring(0, file.name.lastIndexOf('.')) || file.name,
            description: '',
            tags: [],
            status: 'ready',
            progress: 0
        })
    }
}

// 移除文件
const handleFileRemove = (file, list) => {
    fileList.value = list
    const index = uploadItems.value.findIndex(item => item.file.uid === file.uid)
    if (index !== -1) {
        uploadItems.value.splice(index, 1)
    }
}

const removeUploadItem = (index) => {
    const item = uploadItems.value[index]
    const listIndex = fileList.value.findIndex(f => f.uid === item.file.uid)
    if (listIndex !== -1) {
        fileList.value.splice(listIndex, 1)
    }
    uploadItems.value.splice(index, 1)
}

// 文件转 Base64
const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = () => {
            // 去除 "data:xxx/xxx;base64," 前缀
            const result = reader.result.split(',')[1]
            resolve(result)
        }
        reader.onerror = error => reject(error)
    })
}

// 执行批量上传
const startUpload = async () => {
    if (isUploading.value) return
    isUploading.value = true

    let successCount = 0
    let skipCount = 0
    let failCount = 0

    for (const item of uploadItems.value) {
        if (item.status === 'success' || item.status === 'skipped') {
            if (item.status === 'success') successCount++
            if (item.status === 'skipped') skipCount++
            continue
        }

        item.status = 'uploading'
        item.progress = 20

        try {
            const base64Data = await fileToBase64(item.file.raw)
            item.progress = 50

            const payload = {
                category_id: parseInt(props.categoryId),
                filename: item.file.name,
                base64_data: base64Data,
                title: item.title,
                description: item.description,
                tags: item.tags
            }

            const response = await request.post('/get_knowledge/upload_file', payload)

            if (response.data && response.data.success) {
                item.status = 'success'
                item.progress = 100
                successCount++
            } else {
                throw new Error(response.data?.msg || '上传失败')
            }
        } catch (error) {
            const status = error.response?.status
            if (status === 409) {
                item.status = 'skipped'
                item.progress = 100
                skipCount++
                continue
            }
            console.error('上传文件失败:', item.file.name, error)
            item.status = 'error'
            failCount++
            const d = error.response?.data?.detail
            const msg =
                typeof d === 'string'
                    ? d
                    : Array.isArray(d)
                      ? d.map((x) => x.msg || String(x)).join('；')
                      : error.message || '上传失败'
            ElMessage.error(`${item.file.name}：${msg}`)
        }
    }

    isUploading.value = false

    if (failCount === 0) {
        const parts = []
        if (successCount > 0) parts.push(`成功上传 ${successCount} 个`)
        if (skipCount > 0) parts.push(`跳过重复 ${skipCount} 个（内容已存在）`)
        if (parts.length) {
            ElMessage.success(parts.join('，'))
        }
        emit('success')
    } else {
        ElMessage.warning(
            `上传完成。成功 ${successCount} 个，跳过重复 ${skipCount} 个，失败 ${failCount} 个`
        )
    }
}
</script>

<style scoped>
.upload-component {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.upload-area :deep(.el-upload-dragger) {
    border-radius: 0;
    border: 1px dashed #dcdfe6;
}

.upload-list-container {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #ebeef5;
    background-color: #fafbfc;
    padding: 12px;
}

.list-title {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: #303133;
    border-bottom: 1px solid #ebeef5;
    padding-bottom: 8px;
}

.upload-items {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.upload-item-card {
    background: #fff;
    border: 1px solid #e4e7ed;
    padding: 12px;
    position: relative;
}

.item-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
}

.item-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.item-title-input :deep(.el-input-group__prepend) {
    background-color: #f5f7fa;
    color: #909399;
    border-radius: 0;
}

.item-title-input :deep(.el-input__inner) {
    border-radius: 0;
}

.item-desc-input :deep(.el-textarea__inner) {
    border-radius: 0;
    font-size: 12px;
}

.item-tags-select :deep(.el-input__inner) {
    border-radius: 0;
}

.item-status {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
    min-width: 80px;
}

.item-progress {
    margin-top: 8px;
}

.upload-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 12px;
    border-top: 1px solid #ebeef5;
}

.square-btn {
    border-radius: 0;
}

/* 美化滚动条 */
.upload-list-container::-webkit-scrollbar {
    width: 6px;
}

.upload-list-container::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.upload-list-container::-webkit-scrollbar-thumb {
    background: #c1c1c1;
}
</style>
