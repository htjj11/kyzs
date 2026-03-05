<template>
  <div class="new-editor-container">
    <!-- 固定工具栏 -->
    <div v-if="editor" class="toolbar">
      <button
        @click="editor.chain().focus().toggleBold().run()"
        :class="{ 'is-active': editor.isActive('bold') }"
      >
        粗体
      </button>
      <button
        @click="editor.chain().focus().toggleItalic().run()"
        :class="{ 'is-active': editor.isActive('italic') }"
      >
        斜体
      </button>
      <button
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
      >
        H1
      </button>
      <button
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
      >
        H2
      </button>
      <button
        @click="editor.chain().focus().toggleBulletList().run()"
        :class="{ 'is-active': editor.isActive('bulletList') }"
      >
        无序列表
      </button>
      <button
        @click="editor.chain().focus().toggleOrderedList().run()"
        :class="{ 'is-active': editor.isActive('orderedList') }"
      >
        有序列表
      </button>
      <button
        @click="setLink"
      >
        链接
      </button>
      <div class="toolbar-spacer"></div>
      <button class="save-btn" @click="handleSave" :disabled="isSaving">
        {{ isSaving ? '保存中...' : '保存' }}
      </button>
      <button class="close-btn" @click="handleClose">
        关闭
      </button>
    </div>

    <EditorContent :editor="editor" class="editor" />
  
  <!-- AI助手图标 -->
  <div
    v-if="showAIAssistant && editor"
    class="ai-assistant"
    :style="{
      position: 'fixed',
      left: aiPosition.x + 'px',
      top: aiPosition.y + 'px',
      zIndex: 1000
    }"
    @click="generateAI"
  >
    <button 
      class="ai-button"
      :disabled="isGenerating"
      :class="{ 'generating': isGenerating }"
    >
      <span v-if="!isGenerating">🤖</span>
      <span v-else class="loading">⏳</span>
    </button>
  </div>

  <!-- AI编辑对话框 -->
  <el-dialog
    v-model="showAIReviewDialog"
    title="AI智能编辑"
    width="80%"
    :close-on-click-modal="false"
    @close="closeAIReviewDialog"
  >
    <EditReviewAI
      v-if="showAIReviewDialog"
      :selected-text="selectedText"
      @insert-success="handleAIInsertSuccess"
      @close="closeAIReviewDialog"
    />
  </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { Editor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import Heading from '@tiptap/extension-heading';
import BulletList from '@tiptap/extension-bullet-list';
import OrderedList from '@tiptap/extension-ordered-list';
import ListItem from '@tiptap/extension-list-item';
import Link from '@tiptap/extension-link';
import { Markdown } from '@tiptap/markdown';
import { ElMessageBox, ElMessage } from 'element-plus';
import EditReviewAI from '@/components/small/edit_review_ai.vue';
import request from '@/api/request';

// 定义props
const props = defineProps({
  reviewId: {
    type: Number,
    default: null
  },
  reviewData: {
    type: Object,
    default: null
  }
});

// 定义事件
const emit = defineEmits(['close', 'saved']);

const content = ref(''); // 初始化为空字符串

const editor = ref(null);
const isSaving = ref(false);

// 获取现有内容
const fetchExistingContent = () => {
  if (!props.reviewData || !props.reviewData.review_body) return;
  
  content.value = props.reviewData.review_body || '';
  
  // 如果编辑器已初始化，设置内容
  if (editor.value && content.value) {
    editor.value.commands.setContent(content.value);
  }
};

// 保存功能
const handleSave = async () => {
  if (!props.reviewId) {
    ElMessage.error('缺少记录ID，无法保存');
    return;
  }

  if (!editor.value) {
    ElMessage.error('编辑器未初始化');
    return;
  }

  try {
    isSaving.value = true;
    
    // 获取编辑器内容（HTML格式）
    const htmlContent = editor.value.getHTML();
    
    console.log('保存内容:', htmlContent);
    
    // 调用保存接口
    const response = await request.post('/get_review/modify_review_new', {
      review_id: props.reviewId,
      review_body: htmlContent
    });
    
    if (response.data && response.data.code === 200) {
      ElMessage.success('保存成功');
      // 触发保存成功事件
      emit('saved');
    } else {
      throw new Error(response.data?.msg || '保存失败');
    }
  } catch (error) {
    console.error('保存失败:', error);
    ElMessage.error('保存失败: ' + (error.message || '未知错误'));
  } finally {
    isSaving.value = false;
  }
};

const setLink = () => {
  const url = window.prompt('输入链接 URL:');
  if (url) {
    editor.value.chain().focus().setLink({ href: url }).run();
  } else {
    editor.value.chain().focus().unsetLink().run();
  }
};



// AI助手相关功能
const showAIAssistant = ref(false)
const aiPosition = ref({ x: 0, y: 0 })
const selectedText = ref('')
const isGenerating = ref(false)
const showAIReviewDialog = ref(false) // 控制AI编辑窗口显示

const handleSelectionUpdate = () => {
  const selection = editor.value?.state.selection
  if (selection && !selection.empty) {
    // 获取选中文本
    selectedText.value = editor.value?.state.doc.textBetween(
      selection.from,
      selection.to,
      ' '
    ) || ''
    
    // 计算选区的屏幕位置
    const coords = editor.value?.view.coordsAtPos(selection.from)
    if (coords) {
      aiPosition.value = {
        x: coords.left,
        y: coords.top - 40 // 在选区上方显示
      }
      showAIAssistant.value = true
    }
  } else {
    showAIAssistant.value = false
  }
}

const generateAI = async () => {
  if (!selectedText.value || isGenerating.value) return
  
  // 显示AI编辑窗口
  showAIReviewDialog.value = true
}

// 模拟AI接口调用（实际项目中替换为真实API）
// 已删除，因为现在使用 EditReviewAI 组件处理AI功能

// 处理AI编辑成功
const handleAIInsertSuccess = (data) => {
  console.log('AI编辑成功:', data)
  
  if (data && data.summary) {
    // 替换选中文本
    editor.value?.chain().focus().deleteSelection().run()
    editor.value?.chain().focus().insertContent(data.summary).run()
    
    // 隐藏AI助手和弹窗
    showAIAssistant.value = false
    showAIReviewDialog.value = false
    
    ElMessage.success('AI生成内容已替换！')
  }
}

// 处理AI引用插入 - 只用于兼容旧版本，不执行实际操作
const handleAIInsertReference = (summary) => {
  console.log('AI引用插入事件（已废弃）:', summary)
  // 不执行任何操作，避免重复替换
}

// 关闭AI编辑对话框
const closeAIReviewDialog = () => {
  showAIReviewDialog.value = false
  showAIAssistant.value = false
}

// 处理组件关闭
const handleClose = () => {
  emit('close')
}

onMounted(() => {
  // 先获取现有内容
  fetchExistingContent();
  
  editor.value = new Editor({
    content: content.value,
    parseOptions: { preserveWhitespace: 'full' },
    extensions: [
      StarterKit.configure({
        heading: false, // 我们手动加 Heading 以支持更多级别
      }),
      Heading.configure({ levels: [1, 2, 3] }),
      BulletList,
      OrderedList,
      ListItem,
      Link.configure({ openOnClick: false }),
      Markdown.configure({
        html: false,
        tightLists: true,
        bulletListMarker: '-',
      }),
    ],
    onUpdate: () => {
      content.value = editor.value.getMarkdown();
      console.log('Markdown:', content.value);
    },
    onSelectionUpdate: () => {
      // 监听选区变化，显示/隐藏AI助手
      handleSelectionUpdate();
    },
  });
});

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>

<style>
.toolbar {
  position: fixed;
  top: 70px;
  left: 20px;
  right: 20px;
  z-index: 100;
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.toolbar button {
  padding: 8px 12px;
  border: 1px solid #ccc;
  background: white;
  cursor: pointer;
  border-radius: 4px;
}

.toolbar button.is-active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.editor {
  border: 1px solid #ddd;
  min-height: 400px;
  padding: 16px;
  border-radius: 8px;
  background: #fff;
}

.ProseMirror {
  outline: none;
}

.copy-btn {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.copy-btn:hover {
  background-color: #059669;
}

/* AI助手按钮样式 */
.ai-assistant {
  position: fixed;
  pointer-events: auto;
}

.ai-button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  animation: aiPulse 2s infinite;
}

.ai-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.ai-button:active {
  transform: scale(0.95);
}

.ai-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
  animation: none;
}

.ai-button.generating {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.ai-button .loading {
  animation: spin 1s linear infinite;
}

@keyframes aiPulse {
  0% {
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  50% {
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.6);
  }
  100% {
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 新增：全屏编辑器容器样式 */
.new-editor-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  margin: -20px; /* 抵消el-dialog的内边距 */
  padding: 20px;
  box-sizing: border-box;
}

.toolbar-spacer {
  flex: 1;
}

.close-btn {
  background-color: #f56c6c !important;
  color: white !important;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #e85a5a !important;
}

.close-btn:disabled {
  background-color: #c0c4cc !important;
  cursor: not-allowed;
}

.save-btn {
  background-color: #67c23a !important;
  color: white !important;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 8px;
  transition: background-color 0.2s;
}

.save-btn:hover {
  background-color: #5daf34 !important;
}

.save-btn:disabled {
  background-color: #c0c4cc !important;
  cursor: not-allowed;
}

.editor {
  flex: 1;
  border: 1px solid #ddd;
  padding: 16px;
  border-radius: 8px;
  background: #fff;
  margin-top: 100px; /* 为固定工具栏留出空间 */
}
</style>