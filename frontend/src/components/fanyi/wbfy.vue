 <template>
  <div style="width: 100%; min-height: 100%; background: #f5f7fa; padding: 20px; box-sizing: border-box;" class="wbfy-container">
    <!-- 控制面板 -->
    <div style="background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <div style="margin-bottom: 16px;">
        <label style="display: block; margin-bottom: 8px; color: #606266; font-weight: 500;">翻译方向：</label>
        <select v-model="translateType" style="width: 100%; padding: 10px 12px; border: 1px solid #dcdfe6; border-radius: 4px; background: white; color: #606266; font-size: 14px;">
          <option value="en2zh">英文 → 中文</option>
          <option value="zh2en">中文 → 英文</option>
        </select>
      </div>

      <div>
        <label style="display: block; margin-bottom: 8px; color: #606266; font-weight: 500;">专业领域：</label>
        <select v-model="fieldId" style="width: 100%; padding: 10px 12px; border: 1px solid #dcdfe6; border-radius: 4px; background: white; color: #606266; font-size: 14px;">
          <option value="1">石油工程</option>
        </select>
      </div>
    </div>

    <!-- 翻译输入 -->
    <div style="background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <label style="display: block; margin-bottom: 12px; color: #606266; font-weight: 500;">原文输入：</label>
      <textarea
        v-model="inputText"
        placeholder="请输入要翻译的文本..."
        rows="4"
        style="width: 100%; padding: 12px; border: 1px solid #dcdfe6; border-radius: 4px; box-sizing: border-box; font-size: 14px; resize: vertical; min-height: 100px;"
      ></textarea>
    </div>

    <!-- 翻译按钮 -->
    <div style="text-align: center; margin-bottom: 20px;">
      <button
        @click="translateText"
        :disabled="!inputText.trim() || loading"
        :style="{
          padding: '12px 24px',
          margin: '8px 0',
          background: loading || !inputText.trim() ? '#c0c4cc' : '#409eff',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          fontSize: '14px',
          fontWeight: '500',
          cursor: loading || !inputText.trim() ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s'
        }"
        @mouseover="handleButtonHover"
        @mouseout="handleButtonLeave"
      >
        {{ loading ? '翻译中...' : '开始翻译' }}
      </button>
    </div>

    <!-- 翻译结果 -->
    <div style="background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <label style="display: block; margin-bottom: 12px; color: #606266; font-weight: 500;">翻译结果：</label>
      <div style="border: 1px solid #dcdfe6; border-radius: 4px; padding: 12px; min-height: 100px; max-height: 200px; overflow-y: auto; background: #fafafa; word-wrap: break-word; line-height: 1.6;" class="result-area">
        <p v-if="!translateResult" style="color: #909399; font-style: italic; text-align: center; margin: 20px 0;">翻译结果将显示在这里...</p>
        <p v-else style="color: #303133; margin: 0;">{{ translateResult }}</p>
      </div>
    </div>

    <!-- 词汇表 -->
    <div v-if="wordsDict.length > 0" style="background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);">
      <h3 style="color: #303133; margin: 0 0 16px 0; font-size: 16px; font-weight: 600; border-bottom: 1px solid #ebeef5; padding-bottom: 12px;">文中词汇解析</h3>
      <div v-for="word in wordsDict" :key="word.id" style="border: 1px solid #ebeef5; border-radius: 4px; padding: 12px; margin-bottom: 12px; background: #fafafa; transition: all 0.3s;">
        <div style="margin-bottom: 8px;">
          <span style="color: #409eff; font-weight: 500;">{{ word.content1 }}</span>
          <span style="color: #606266; margin: 0 8px;">→</span>
          <span style="color: #303133; font-weight: 500;">{{ word.content2 }}</span>
          <span style="color: #909399; margin-left: 8px;">【</span>
          <strong style="color: #e6a23c;">{{ word.from }}</strong>
          <span style="color: #909399;">】</span>
        </div>
        <p style="color: #606266; margin: 0; font-size: 14px; line-height: 1.5;">{{ word.content3 }}</p>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" style="background: #fef0f0; border: 1px solid #fde2e2; border-radius: 4px; padding: 12px; margin: 8px 0; word-wrap: break-word;">
      <span style="color: #f56c6c; font-size: 14px; font-weight: 500;">⚠ {{ error }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import request from "@/api/request.js";

// 响应式数据
const inputText = ref('')
const translateResult = ref('')
const wordsDict = ref([])
const translateType = ref('en2zh')
const fieldId = ref(1)
const loading = ref(false)
const error = ref('')

// 按钮悬停状态
const buttonHover = ref(false)

// 按钮悬停效果处理
const handleButtonHover = () => {
  buttonHover.value = true
}

const handleButtonLeave = () => {
  buttonHover.value = false
}

// 翻译函数
const translateText = async () => {
  if (!inputText.value.trim()) {
    error.value = '请输入要翻译的文本'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const response = await request.post('/translate/translate_text', {
        text: inputText.value,
        translate_type: translateType.value,
        field_id: fieldId.value
      });

    const data = await response.data
    console.log(data)
    translateResult.value = data.translate_result
    wordsDict.value = data.words_dict || []
    
  } catch (err) {
    error.value = '翻译失败，基于大模型翻译小概率会出现结构错误，可稍后再试'+err
    console.error('Translation error:', err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 自定义滚动条样式 */
.wbfy-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.wbfy-container::-webkit-scrollbar-track {
  background: rgba(64, 158, 255, 0.1);
  border-radius: 4px;
}

.wbfy-container::-webkit-scrollbar-thumb {
  background: rgba(64, 158, 255, 0.6);
  border-radius: 4px;
  transition: background 0.3s;
}

.wbfy-container::-webkit-scrollbar-thumb:hover {
  background: rgba(64, 158, 255, 0.8);
}

/* 内部滚动条（翻译结果区域）样式 */
.result-area::-webkit-scrollbar {
  width: 6px;
}

.result-area::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.result-area::-webkit-scrollbar-thumb {
  background: rgba(64, 158, 255, 0.4);
  border-radius: 3px;
}

.result-area::-webkit-scrollbar-thumb:hover {
  background: rgba(64, 158, 255, 0.6);
}
</style>