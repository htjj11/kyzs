<template>
  <div class="translation-wrapper">
    <div class="translation-container scientific-card">
      <!-- 顶部控制条 -->
      <div class="translation-header">
        <div class="language-controls">
          <el-select v-model="sourceLang" class="lang-select" size="large">
            <el-option label="自动检测 / 英文" value="en" />
            <el-option label="中文" value="zh" />
          </el-select>

          <el-button class="swap-btn" circle @click="swapLanguages">
            <el-icon>
              <Switch />
            </el-icon>
          </el-button>

          <el-select v-model="targetLang" class="lang-select" size="large">
            <el-option label="中文" value="zh" />
            <el-option label="英文" value="en" />
          </el-select>
        </div>

        <div class="field-selector">
          <span class="field-label">专业领域：</span>
          <el-select v-model="fieldId" class="field-select" size="default">
            <el-option label="石油工程" :value="1" />
            <el-option label="通用领域" :value="0" />
            <el-option label="地质勘探" :value="2" />
          </el-select>
        </div>
      </div>

      <!-- 核心翻译区 -->
      <div class="translation-main">
        <!-- 输入区 -->
        <div class="pane input-pane">
          <div class="pane-header">
            <span class="pane-title">原文输入</span>
            <el-button v-if="inputText" type="info" link @click="clearInput">
              <el-icon>
                <Delete />
              </el-icon> 清空
            </el-button>
          </div>
          <el-input v-model="inputText" type="textarea" :rows="12" placeholder="请输入要翻译的内容..."
            class="scientific-textarea" resize="none" />
          <div class="char-count">{{ inputText.length }} / 5000</div>

          <div class="action-footer">
            <el-button type="primary" class="translate-trigger-btn" :loading="loading" :disabled="!inputText.trim()"
              @click="translateText">
              {{ loading ? '翻译中' : '开始翻译' }}
            </el-button>
          </div>
        </div>

        <!-- 输出区 -->
        <div class="pane output-pane" v-loading="loading" element-loading-background="rgba(255, 255, 255, 0.7)">
          <div class="pane-header">
            <span class="pane-title">翻译结果</span>
            <el-button v-if="translateResult" type="primary" link @click="copyToClipboard">
              <el-icon>
                <CopyDocument />
              </el-icon> 复制内容
            </el-button>
          </div>
          <div class="result-content" :class="{ 'has-content': translateResult }">
            <template v-if="translateResult">
              {{ translateResult }}
            </template>
            <div v-else class="empty-placeholder">
              翻译结果将显示在这里...
            </div>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <el-alert v-if="error" :title="error" type="error" show-icon :closable="true" class="error-alert"
        @close="error = ''" />
    </div>

    <!-- 词汇解析区 -->
    <div v-if="wordsDict.length > 0" class="glossary-section">
      <div class="glossary-header">
        <el-icon class="header-icon">
          <Collection />
        </el-icon>
        <span>文中专业词汇解析</span>
      </div>
      <div class="glossary-grid">
        <div v-for="word in wordsDict" :key="word.id" class="glossary-card scientific-card">
          <div class="word-pair">
            <span class="word-source">{{ word.content1 }}</span>
            <el-icon class="arrow-icon">
              <Right />
            </el-icon>
            <span class="word-target">{{ word.content2 }}</span>
          </div>
          <div class="word-def-container">
            <p class="word-def">{{ word.content3 }}</p>
          </div>
          <div class="word-origin">
            <span class="origin-label">来源：{{ word.from }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Switch, CopyDocument, Delete, Collection, Right } from '@element-plus/icons-vue'
import request from "@/api/request.js"

// 响应式数据
const inputText = ref('')
const translateResult = ref('')
const wordsDict = ref([])
const sourceLang = ref('en')
const targetLang = ref('zh')
const fieldId = ref(1)
const loading = ref(false)
const error = ref('')

// 语言切换
const swapLanguages = () => {
  const temp = sourceLang.value
  sourceLang.value = targetLang.value
  targetLang.value = temp
  // 这里可以根据业务逻辑决定是否立即重新翻译
}

// 清空
const clearInput = () => {
  inputText.value = ''
  translateResult.value = ''
  wordsDict.value = []
}

// 复制到剪贴板
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(translateResult.value)
    ElMessage.success('已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败，请手动选择复制')
  }
}

// 翻译函数
const translateText = async () => {
  if (!inputText.value.trim()) return

  loading.value = true
  error.value = ''

  // 构造翻译类型字符串，接口期望 en2zh 或 zh2en
  const translateType = `${sourceLang.value}2${targetLang.value}`

  try {
    const response = await request.post('/translate/translate_text', {
      text: inputText.value,
      translate_type: translateType,
      field_id: fieldId.value
    });

    if (response.data && (response.data.code === 200 || response.data.translate_result)) {
      translateResult.value = response.data.translate_result
      wordsDict.value = response.data.words_dict || []
    } else {
      throw new Error(response.data?.msg || '翻译异常')
    }

  } catch (err) {
    error.value = '翻译失败，请检查网络或稍后再试：' + (err.message || err)
    console.error('Translation error:', err)
  } finally {
    loading.value = false
  }
}

// 监听语言变化自动更新 translate_type 逻辑已在 translateText 中处理
</script>

<style scoped>
.translation-wrapper {
  padding: 0;
  /* 交给父卡片控制边距 */
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  background-color: transparent;
  /* 融入底部的液态玻璃 */
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', sans-serif;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  /* 如果出现词汇表则内部滚动 */
}

.scientific-card {
  background: transparent;
  border: none;
  box-shadow: none;
}

.translation-container {
  display: flex;
  flex-direction: column;
  flex: 1;
}

/* 顶部栏 */
.translation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  background-color: transparent;
}

.language-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.lang-select {
  width: 160px;
}

.swap-btn {
  color: #3f88f2;
}

.field-selector {
  display: flex;
  align-items: center;
}

.field-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.field-select {
  width: 140px;
}

/* 核心区域 */
.translation-main {
  display: flex;
  flex: 1;
}

.pane {
  flex: 1;
  padding: 24px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-y: auto;
}

.input-pane {
  border-right: 1px solid #ebeef5;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.pane-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.scientific-textarea :deep(.el-textarea__inner) {
  border: none;
  padding: 0;
  font-size: 16px;
  line-height: 1.6;
  color: #2c3e50;
  background: transparent;
  box-shadow: none !important;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #909399;
  margin-top: 12px;
}

.action-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.translate-trigger-btn {
  padding: 12px 40px;
  font-size: 16px;
  border-radius: 2px;
  background-color: #3f88f2;
  border-color: #3f88f2;
}

.output-pane {
  background-color: rgba(250, 251, 252, 0.4);
}

.result-content {
  font-size: 16px;
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  flex: 1;
  min-height: 200px;
}

.result-content.has-content {
  color: #1a1a1a;
}

.empty-placeholder {
  color: #909399;
  font-style: italic;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.error-alert {
  margin: 10px 24px 20px;
  border-radius: 2px;
}

/* 词汇表 */
.glossary-section {
  margin-top: 30px;
}

.glossary-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 4px;
}

.header-icon {
  color: #3f88f2;
}

.glossary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.glossary-card {
  padding: 18px;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  position: relative;
  min-height: 100px;
}

.glossary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.word-pair {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.word-source {
  color: #3f88f2;
  font-weight: 700;
  font-size: 18px;
}

.arrow-icon {
  margin: 0 10px;
  color: #c0c4cc;
  font-size: 14px;
}

.word-target {
  color: #303133;
  font-weight: 700;
  font-size: 18px;
}

.word-def-container {
  flex: 1;
}

.word-def {
  font-size: 15px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.word-origin {
  margin-top: 12px;
  text-align: right;
  border-top: 1px dashed #ebeef5;
  padding-top: 8px;
}

.origin-label {
  font-size: 11px;
  color: #909399;
  font-style: italic;
}

.square-tag {
  border-radius: 2px;
}

/* 响应式 */
@media (max-width: 900px) {
  .translation-main {
    flex-direction: column;
  }

  .input-pane {
    border-right: none;
    border-bottom: 1px solid #ebeef5;
  }

  .translation-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}
</style>