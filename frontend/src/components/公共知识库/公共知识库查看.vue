<template>
    <div v-loading="loading" class="file-view-container">
        <div v-if="fileData" class="view-split-layout">
            <!-- 左侧：基本信息 -->
            <div class="view-left">
                <div class="section-title">基本信息</div>
                <div class="info-grid">
                    <div class="info-item full-width" v-if="fileData.category_path && fileData.category_path.length > 0">
                        <span class="info-label">存储目录</span>
                        <span class="info-value">{{ fileData.category_path.join(' / ') }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">文件名</span>
                        <span class="info-value">{{ getFileName(fileData.file_path) }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">文件ID</span>
                        <span class="info-value">#{{ fileData.id }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">文件类型</span>
                        <span class="info-value">{{ fileData.file_type }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">文件大小</span>
                        <span class="info-value">{{ (fileData.file_size / 1024).toFixed(2) }} KB</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">上传时间</span>
                        <span class="info-value">{{ fileData.created_at }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">最后更新</span>
                        <span class="info-value">{{ fileData.updated_at }}</span>
                    </div>
                </div>
            </div>

            <!-- 右侧：描述、标签与操作 -->
            <div class="view-right">
                <div class="section-group">
                    <div class="section-title">文档描述</div>
                    <div class="description-box">
                        {{ fileData.description || '暂无描述' }}
                    </div>
                </div>

                <div class="section-group">
                    <div class="section-title">标签属性</div>
                    <div class="tags-container">
                        <el-tag v-for="tag in parsedTags" :key="tag" size="small" effect="plain" class="tag-item">
                            {{ tag }}
                        </el-tag>
                        <span v-if="!fileData.tags || parsedTags.length === 0" class="no-tags">暂无标签</span>
                    </div>
                </div>

                <div class="view-actions">
                    <el-button type="primary" class="square-btn" @click="downloadFile">
                        下载此文档
                    </el-button>
                    <el-button @click="$emit('close')" class="square-btn">
                        关闭详情
                    </el-button>
                </div>
            </div>
        </div>

        <el-empty v-else-if="!loading" description="未找到文件内容" />
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import request from '@/api/request'

const props = defineProps({
    fileId: {
        type: Number,
        required: true
    }
})

const emit = defineEmits(['close'])

const loading = ref(false)
const fileData = ref(null)

// 解析标签
const parsedTags = computed(() => {
    if (!fileData.value || !fileData.value.tags) return []
    try {
        return JSON.parse(fileData.value.tags)
    } catch (e) {
        console.warn('解析标签失败:', e)
        return []
    }
})

// 获取文件名
const getFileName = (path) => {
    if (!path) return '未知'
    return path.split(/[/\\]/).pop().split('_').slice(1).join('_') || path.split(/[/\\]/).pop()
}

// 获取详情
const fetchDetail = async () => {
    loading.value = true
    try {
        const response = await request.post('/public_knowledgebase/get_public_file_by_id', {
            file_id: props.fileId
        })

        if (response.data && response.data.code === 200 && response.data.data.length > 0) {
            fileData.value = response.data.data[0]
        } else {
            ElMessage.error(response.data?.msg || '获取文件详情失败')
        }
    } catch (error) {
        console.error('获取文件详情错误:', error)
        ElMessage.error('网络错误，请稍后重试')
    } finally {
        loading.value = false
    }
}

// 下载逻辑
const downloadFile = () => {
    if (!fileData.value || !fileData.value.file_base64) {
        ElMessage.error('无法获取文件内容')
        return
    }

    try {
        const base64Data = fileData.value.file_base64
        const byteCharacters = atob(base64Data)
        const byteNumbers = new Array(byteCharacters.length)
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i)
        }
        const byteArray = new Uint8Array(byteNumbers)
        const blob = new Blob([byteArray])

        const fileName = getFileName(fileData.value.file_path)
        const downloadLink = document.createElement('a')
        const url = window.URL.createObjectURL(blob)

        downloadLink.href = url
        downloadLink.download = fileName
        document.body.appendChild(downloadLink)
        downloadLink.click()

        document.body.removeChild(downloadLink)
        window.URL.revokeObjectURL(url)

        ElMessage.success('文档已开始下载')
    } catch (error) {
        console.error('下载失败:', error)
        ElMessage.error('下载过程中发生错误')
    }
}

onMounted(() => {
    fetchDetail()
})
</script>

<style scoped>
.file-view-container {
    min-height: 380px;
}

.view-split-layout {
    display: flex;
    gap: 24px;
}

.view-left {
    flex: 1.2;
    padding-right: 24px;
    border-right: 1px solid #ebeef5;
}

.view-right {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.section-title {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 16px;
    padding-left: 8px;
    border-left: 3px solid #409eff;
}

.section-group {
    margin-bottom: 24px;
}

.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.info-item {
    display: flex;
    flex-direction: column;
}

.info-item.full-width {
    grid-column: span 2;
}

.info-label {
    font-size: 12px;
    color: #909399;
}

.info-value {
    font-size: 13px;
    color: #303133;
    word-break: break-all;
}

.description-box {
    background: #f8f9fb;
    padding: 12px;
    border-radius: 4px;
    font-size: 13px;
    color: #606266;
    line-height: 1.6;
    min-height: 80px;
    border: 1px solid #e4e7ed;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.tag-item {
    border-radius: 0;
}

.no-tags {
    font-size: 12px;
    color: #909399;
    font-style: italic;
}

.view-actions {
    margin-top: 12px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    border-top: 1px solid #ebeef5;
    padding-top: 20px;
}

.square-btn {
    border-radius: 0;
}
</style>
