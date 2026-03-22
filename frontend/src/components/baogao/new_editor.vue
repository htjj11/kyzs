<template>
  <div class="new-editor-container">
    <div class="editor-layout">

      <!-- 头部工具栏 -->
      <div v-if="editor" class="toolbar">
        <div class="toolbar-group">
          <!-- 撤销/重做 -->
          <el-button-group class="square-group">
            <el-button class="square-btn toolbar-btn" :disabled="!editor.can().undo()"
              @click="editor.chain().focus().undo().run()" title="撤销">
              <el-icon>
                <RefreshLeft />
              </el-icon>
            </el-button>
            <el-button class="square-btn toolbar-btn" :disabled="!editor.can().redo()"
              @click="editor.chain().focus().redo().run()" title="重做">
              <el-icon>
                <RefreshRight />
              </el-icon>
            </el-button>
          </el-button-group>
        </div>

        <div class="toolbar-divider"></div>

        <div class="toolbar-group">
          <!-- 字体样式 -->
          <button class="toolbar-btn" :class="{ 'is-active': editor.isActive('bold') }"
            @click="editor.chain().focus().toggleBold().run()" title="粗体">
            <span style="font-weight: 800; font-family: 'Times New Roman', serif;">B</span>
          </button>
          <button class="toolbar-btn" :class="{ 'is-active': editor.isActive('italic') }"
            @click="editor.chain().focus().toggleItalic().run()" title="斜体">
            <span style="font-style: italic; font-family: 'Times New Roman', serif;">I</span>
          </button>
          <button class="toolbar-btn" :class="{ 'is-active': editor.isActive('strike') }"
            @click="editor.chain().focus().toggleStrike().run()" title="删除线">
            <span style="text-decoration: line-through; font-family: 'Times New Roman', serif;">S</span>
          </button>
        </div>

        <div class="toolbar-divider"></div>

        <div class="toolbar-group">
          <!-- 标题格式 -->
          <button class="toolbar-btn text-btn" :class="{ 'is-active': editor.isActive('heading', { level: 1 }) }"
            @click="editor.chain().focus().toggleHeading({ level: 1 }).run()">H1</button>
          <button class="toolbar-btn text-btn" :class="{ 'is-active': editor.isActive('heading', { level: 2 }) }"
            @click="editor.chain().focus().toggleHeading({ level: 2 }).run()">H2</button>
          <button class="toolbar-btn text-btn" :class="{ 'is-active': editor.isActive('heading', { level: 3 }) }"
            @click="editor.chain().focus().toggleHeading({ level: 3 }).run()">H3</button>
        </div>

        <div class="toolbar-divider"></div>

        <div class="toolbar-group">
          <!-- 列表与引用 -->
          <button class="toolbar-btn" :class="{ 'is-active': editor.isActive('bulletList') }"
            @click="editor.chain().focus().toggleBulletList().run()" title="无序列表">
            <el-icon>
              <List />
            </el-icon>
          </button>
          <button class="toolbar-btn text-btn" style="font-weight: bold;"
            :class="{ 'is-active': editor.isActive('orderedList') }"
            @click="editor.chain().focus().toggleOrderedList().run()" title="有序列表">
            1.
          </button>
          <button class="toolbar-btn" :class="{ 'is-active': editor.isActive('blockquote') }"
            @click="editor.chain().focus().toggleBlockquote().run()" title="引用段落">
            <el-icon>
              <ChatLineSquare />
            </el-icon>
          </button>
        </div>

        <div class="toolbar-divider"></div>

        <div class="toolbar-group">
          <!-- 其他组件 -->
          <button class="toolbar-btn" :class="{ 'is-active': editor.isActive('link') }" @click="setLink" title="插入链接">
            <el-icon>
              <Link />
            </el-icon>
          </button>
          <button class="toolbar-btn text-btn" @click="editor.chain().focus().setHorizontalRule().run()"
            title="分割线">—</button>
        </div>

        <div class="toolbar-spacer"></div>

        <div class="toolbar-group actions">
          <!-- 操作 -->
          <el-button type="primary" class="square-btn action-btn" :loading="isSaving" @click="handleSave">
            <el-icon>
              <Check />
            </el-icon> {{ isSaving ? '保存中...' : '提交保存' }}
          </el-button>
          <el-button type="info" plain class="square-btn action-btn" @click="handleClose">
            <el-icon>
              <Close />
            </el-icon> 结束编辑
          </el-button>
        </div>
      </div>

      <!-- 编辑器本体 -->
      <div class="editor-body wrapper-bg">
        <EditorContent :editor="editor" class="scientific-editor" />
      </div>

    </div>

    <!-- AI助手悬浮图标 -->
    <div v-if="showAIAssistant && editor" class="ai-assistant" :style="{
      position: 'fixed',
      left: aiPosition.x + 'px',
      top: aiPosition.y + 'px',
      zIndex: 1000
    }" @click="generateAI">
      <button class="ai-button square-icon" :disabled="isGenerating" :class="{ 'generating': isGenerating }"
        title="AI 智能编辑">
        <span v-if="!isGenerating"><el-icon>
            <Cpu />
          </el-icon></span>
        <span v-else class="loading"><el-icon>
            <Loading />
          </el-icon></span>
      </button>
    </div>

    <!-- AI编辑对话框 -->
    <el-dialog v-model="showAIReviewDialog" title="AI智能编辑" width="95%" top="2vh" :close-on-click-modal="false"
      class="square-dialog" @close="closeAIReviewDialog">
      <EditReviewAI v-if="showAIReviewDialog" :selected-text="selectedText" @insert-success="handleAIInsertSuccess"
        @close="closeAIReviewDialog" />
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
import LinkExtension from '@tiptap/extension-link';
import { Markdown } from '@tiptap/markdown';
import { ElMessageBox, ElMessage, ElButtonGroup, ElButton, ElIcon, ElDialog } from 'element-plus';
import { Check, Close, RefreshLeft, RefreshRight, List, Link, ChatLineSquare, Cpu, Loading } from '@element-plus/icons-vue';
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

const content = ref('');

const editor = ref(null);
const isSaving = ref(false);

// 获取现有内容
const fetchExistingContent = () => {
  if (!props.reviewData || !props.reviewData.review_body) return;

  content.value = props.reviewData.review_body || '';

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

    const response = await request.post('/get_review/modify_review_new', {
      review_id: props.reviewId,
      review_body: htmlContent
    });

    if (response.data && response.data.code === 200) {
      ElMessage.success('保存成功');
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
const showAIReviewDialog = ref(false)

const handleSelectionUpdate = () => {
  const selection = editor.value?.state.selection
  if (selection && !selection.empty) {
    selectedText.value = editor.value?.state.doc.textBetween(
      selection.from,
      selection.to,
      ' '
    ) || ''

    const coords = editor.value?.view.coordsAtPos(selection.from)
    if (coords) {
      aiPosition.value = {
        x: coords.left,
        y: coords.top - 45
      }
      showAIAssistant.value = true
    }
  } else {
    showAIAssistant.value = false
  }
}

const generateAI = async () => {
  if (!selectedText.value || isGenerating.value) return
  showAIReviewDialog.value = true
}

const handleAIInsertSuccess = (data) => {
  console.log('AI编辑成功:', data)

  if (data && data.summary) {
    editor.value?.chain().focus().deleteSelection().run()
    editor.value?.chain().focus().insertContent(data.summary).run()

    showAIAssistant.value = false
    showAIReviewDialog.value = false

    ElMessage.success('AI生成内容已替换！')
  }
}
const closeAIReviewDialog = () => {
  showAIReviewDialog.value = false
  showAIAssistant.value = false
}

const handleClose = () => {
  emit('close')
}

onMounted(() => {
  fetchExistingContent();

  editor.value = new Editor({
    content: content.value,
    parseOptions: { preserveWhitespace: 'full' },
    extensions: [
      StarterKit.configure({
        heading: false,
      }),
      Heading.configure({ levels: [1, 2, 3] }),
      BulletList,
      OrderedList,
      ListItem,
      LinkExtension.configure({ openOnClick: false }),
      Markdown.configure({
        html: false,
        tightLists: true,
        bulletListMarker: '-',
      }),
    ],
    onUpdate: () => {
      content.value = editor.value.getMarkdown();
    },
    onSelectionUpdate: () => {
      handleSelectionUpdate();
    },
  });
});

onBeforeUnmount(() => {
  editor.value?.destroy();
});
</script>

<style scoped>
.new-editor-container {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  background-color: #ffffff;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

.editor-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  margin: 0;
}

/* 基础卡片类 */
.scientific-card {
  background-color: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

/* 头部工具栏 */
.toolbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  padding: 12px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 4px;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background-color: #dcdfe6;
  margin: 0 8px;
}

.toolbar-spacer {
  flex: 1;
}

/* 按钮基础样式覆盖 */
.square-btn {
  border-radius: 2px !important;
}

.square-group .el-button {
  border-radius: 2px !important;
  padding: 8px 12px;
}

/* Tiptap 工具按钮 */
.toolbar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid transparent;
  background: transparent;
  color: #606266;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 15px;
}

.toolbar-btn:hover {
  background-color: #e4e7ed;
  color: #3f88f2;
}

.toolbar-btn.is-active {
  background-color: #ecf5ff;
  color: #3f88f2;
  border-color: #b3d8ff;
  font-weight: bold;
}

.text-btn {
  font-family: 'Times New Roman', serif;
  font-weight: 600;
  font-size: 14px;
}

/* 操作按钮 */
.action-btn {
  min-width: 100px;
}

/* 编辑器正文区 */
.editor-body.wrapper-bg {
  flex: 1;
  padding: 0;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
}

.scientific-editor {
  flex: 1;
  background-color: #ffffff;
  border: none;
  padding: 40px 15%;
  min-height: 500px;
}

/* Tiptap内部样式调整 - 仿科研论文排版 */
.scientific-editor :deep(.ProseMirror) {
  outline: none;
  font-family: 'Times New Roman', SimSun, 'Songti SC', serif;
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
  min-height: 100%;
}

.scientific-editor :deep(.ProseMirror p) {
  margin-top: 0.8em;
  margin-bottom: 0.8em;
  text-align: justify;
}

.scientific-editor :deep(.ProseMirror h1),
.scientific-editor :deep(.ProseMirror h2),
.scientific-editor :deep(.ProseMirror h3) {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', sans-serif;
  color: #1f2f3f;
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  font-weight: 600;
}

.scientific-editor :deep(.ProseMirror h1) {
  font-size: 24px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.scientific-editor :deep(.ProseMirror h2) {
  font-size: 20px;
}

.scientific-editor :deep(.ProseMirror h3) {
  font-size: 18px;
}

.scientific-editor :deep(.ProseMirror blockquote) {
  border-left: 4px solid #c0c4cc;
  padding-left: 16px;
  margin-left: 0;
  color: #606266;
  background-color: #f8f9fa;
  padding: 12px 16px;
}

.scientific-editor :deep(.ProseMirror ul),
.scientific-editor :deep(.ProseMirror ol) {
  padding-left: 2em;
  margin-bottom: 1em;
}

.scientific-editor :deep(.ProseMirror hr) {
  border: none;
  border-top: 1px solid #dcdfe6;
  margin: 2em 0;
}

/* AI助手图标特效 */
.ai-assistant {
  pointer-events: auto;
}

.ai-button.square-icon {
  width: 36px;
  height: 36px;
  border-radius: 2px;
  /* 方正风格 */
  border: 1px solid #3f88f2;
  background: #ffffff;
  color: #3f88f2;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(63, 136, 242, 0.2);
  transition: all 0.2s ease;
}

.ai-button.square-icon:hover {
  background-color: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(63, 136, 242, 0.3);
}

.ai-button.square-icon.generating {
  background-color: #f4f4f5;
  border-color: #909399;
  color: #909399;
}

.loading {
  animation: spin 1s linear infinite;
  display: inline-flex;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* 覆盖全屏弹窗基础样式 */
:deep(.square-dialog .el-dialog) {
  border-radius: 2px;
}

:deep(.square-dialog .el-dialog__header) {
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  margin-right: 0;
  padding: 16px 24px;
}

:deep(.square-dialog .el-dialog__title) {
  font-weight: 600;
  color: #303133;
}
</style>