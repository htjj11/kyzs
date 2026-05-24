<template>
  <div class="new-editor-container">

    <!-- 模板名称（仅模板模式） -->
    <div v-if="!readOnly && mode === 'template'" class="editor-topbar">
      <div class="template-name-area">
        <label class="template-name-label">模板名称：</label>
        <el-input v-model="templateName" placeholder="请输入模板名称" class="template-name-input" />
      </div>
    </div>

    <!-- 编辑区 + 右侧操作栏 -->
    <div class="editor-workspace">
      <div class="editor-main">
        <Editor v-model="editorContent" :init="editorInit" license-key="gpl" />
      </div>

      <aside v-if="!readOnly" class="editor-action-panel">
        <div class="action-panel-title">操作</div>
        <div class="action-panel-buttons">
          <el-button
            type="warning"
            plain
            class="square-btn panel-btn"
            :disabled="!selectedText"
            @click="showAIReviewDialog = true"
          >
            <el-icon><Cpu /></el-icon>
            AI 编辑选中
          </el-button>
          <el-button
            type="primary"
            :loading="isSaving"
            class="square-btn panel-btn"
            @click="handleSave"
          >
            <el-icon><Check /></el-icon>
            {{ isSaving ? '保存中...' : '提交保存' }}
          </el-button>
          <el-button type="info" plain class="square-btn panel-btn" @click="handleClose">
            <el-icon><Close /></el-icon>
            结束编辑
          </el-button>
        </div>
      </aside>
    </div>

    <!-- AI 编辑对话框 -->
    <el-dialog
      v-model="showAIReviewDialog"
      title="AI智能编辑"
      width="95%"
      top="2vh"
      :close-on-click-modal="false"
      class="square-dialog"
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
import { ref, computed } from 'vue';

// TinyMCE Vue 组件
import Editor from '@tinymce/tinymce-vue';

// TinyMCE 核心（自托管，无需 CDN）
import 'tinymce/tinymce';
import 'tinymce/models/dom';
import 'tinymce/themes/silver';
import 'tinymce/icons/default';

// TinyMCE 插件
import 'tinymce/plugins/advlist';
import 'tinymce/plugins/autolink';
import 'tinymce/plugins/lists';
import 'tinymce/plugins/link';
import 'tinymce/plugins/charmap';
import 'tinymce/plugins/searchreplace';
import 'tinymce/plugins/visualblocks';
import 'tinymce/plugins/code';
import 'tinymce/plugins/fullscreen';
import 'tinymce/plugins/insertdatetime';
import 'tinymce/plugins/table';
import 'tinymce/plugins/wordcount';

// TinyMCE 皮肤 CSS（全局引入 UI 皮肤样式）
import 'tinymce/skins/ui/oxide/skin.min.css';
import contentCss from 'tinymce/skins/content/default/content.min.css?inline';

import { ElMessage, ElButton, ElIcon, ElDialog, ElInput } from 'element-plus';
import { Check, Close, Cpu } from '@element-plus/icons-vue';
import EditReviewAI from '@/components/small/edit_review_ai.vue';
import request from '@/api/request';
import { getUserIdFromCookie } from '@/utils/authUtils';

// ---------- Props ----------
const props = defineProps({
  reviewId: {
    type: Number,
    default: null
  },
  reviewData: {
    type: Object,
    default: null
  },
  mode: {
    type: String,
    default: 'review' // 'review' 或 'template'
  },
  readOnly: {
    type: Boolean,
    default: false
  }
});

// ---------- Events ----------
const emit = defineEmits(['close', 'saved']);

// ---------- 状态 ----------
// 根据 mode 和 reviewData 初始化内容
const editorContent = ref(
  props.mode === 'template'
    ? (props.reviewData?.content || '')
    : (props.reviewData?.review_body || '')
);

const templateName = ref(
  props.mode === 'template' ? (props.reviewData?.name || '') : ''
);

const isSaving = ref(false);
const selectedText = ref('');
const showAIReviewDialog = ref(false);

// ---------- TinyMCE 初始化配置 ----------
const editorInit = computed(() => ({
  // GPL 自托管许可（免费版无需 API Key）
  license_key: 'gpl',

  // 关闭外部皮肤加载，使用内联导入的 CSS 字符串
  skin: false,
  content_css: false,

  // 正文排版样式（仿科研论文风格）
  content_style: contentCss + `
    body {
      font-family: 'Times New Roman', SimSun, 'Songti SC', serif;
      font-size: 16px;
      line-height: 1.8;
      color: #2c3e50;
      max-width: 860px;
      margin: 0 auto;
      padding: 40px 48px;
      background: #ffffff;
    }
    p { margin-top: 0.8em; margin-bottom: 0.8em; text-align: justify; }
    h1 {
      font-size: 24px;
      border-bottom: 1px solid #ebeef5;
      padding-bottom: 8px;
    }
    h2 { font-size: 20px; }
    h3 { font-size: 18px; }
    h1, h2, h3 {
      font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
      color: #1f2f3f;
      margin-top: 1.5em;
      margin-bottom: 0.8em;
      font-weight: 600;
    }
    blockquote {
      border-left: 4px solid #c0c4cc;
      padding: 12px 16px;
      margin: 1em 0;
      color: #606266;
      background: #f8f9fa;
    }
    table { border-collapse: collapse; width: 100%; margin: 1em 0; }
    td, th { border: 1px solid #dcdfe6; padding: 12px; }
    th { background: #f5f7fa; font-weight: 600; }
    hr { border: none; border-top: 1px solid #dcdfe6; margin: 2em 0; }
    ul, ol { padding-left: 2em; margin-bottom: 1em; }
    li { margin-bottom: 0.4em; }
    code {
      background: #f4f4f5;
      padding: 2px 6px;
      border-radius: 2px;
      font-family: Consolas, monospace;
      font-size: 0.9em;
      color: #e65c5c;
    }
    pre {
      background: #282c34;
      color: #abb2bf;
      padding: 16px;
      border-radius: 4px;
      overflow-x: auto;
      font-family: Consolas, monospace;
    }
  `,

  // 编辑器高度（fill 父容器）
  height: '100%',
  resize: false,

  // 只读模式关闭菜单栏与工具栏
  menubar: props.readOnly
    ? false
    : 'file edit view insert format tools table',

  toolbar: props.readOnly
    ? false
    : 'undo redo | styles | bold italic underline strikethrough | forecolor backcolor | ' +
      'alignleft aligncenter alignright alignjustify | ' +
      'bullist numlist | outdent indent | blockquote | ' +
      'link table | searchreplace code fullscreen | wordcount',

  plugins: props.readOnly
    ? []
    : [
        'advlist', 'autolink', 'lists', 'link', 'charmap',
        'searchreplace', 'visualblocks', 'code', 'fullscreen',
        'insertdatetime', 'table', 'wordcount'
      ],

  // 只读模式不可编辑
  readonly: props.readOnly,

  // 关闭底部状态栏（只读时）
  statusbar: !props.readOnly,

  // 关闭 TinyMCE 品牌标志与推广提示
  branding: false,
  promotion: false,

  // 监听选区变化 → 更新 selectedText 以驱动 AI 按钮
  setup(editor) {
    editor.on('SelectionChange', () => {
      if (props.readOnly) return;
      const sel = editor.selection.getContent({ format: 'text' }).trim();
      selectedText.value = sel;
    });
  }
}));

// ---------- 保存逻辑 ----------
const handleSave = async () => {
  try {
    isSaving.value = true;
    const htmlContent = editorContent.value;

    let response;
    if (props.mode === 'template') {
      if (!templateName.value.trim()) {
        ElMessage.warning('请输入模板名称');
        return;
      }
      response = await request.post('/report/edit_template', {
        user_id: getUserIdFromCookie(),
        template_id: props.reviewId,
        template_name: templateName.value.trim(),
        template_content: htmlContent
      });
    } else {
      if (!props.reviewId) {
        ElMessage.error('缺少记录ID，无法保存');
        return;
      }
      response = await request.post('/report/modify_review_new', {
        review_id: props.reviewId,
        review_body: htmlContent
      });
    }

    if (response.data?.code === 200) {
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

// ---------- AI 助手逻辑 ----------
const handleAIInsertSuccess = (data) => {
  if (data?.summary) {
    // 通过 TinyMCE 全局实例替换当前选中内容
    const tinyEditor = window.tinymce?.activeEditor;
    if (tinyEditor) {
      tinyEditor.selection.setContent(data.summary);
    }
    selectedText.value = '';
    showAIReviewDialog.value = false;
    ElMessage.success('AI生成内容已替换！');
  }
};

const closeAIReviewDialog = () => {
  showAIReviewDialog.value = false;
};

const handleClose = () => {
  emit('close');
};
</script>

<style scoped>
.new-editor-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  overflow: hidden;
}

/* 模板名称栏 */
.editor-topbar {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.template-name-area {
  display: flex;
  align-items: center;
  gap: 8px;
}

.template-name-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  white-space: nowrap;
}

.template-name-input {
  width: 300px;
}

.square-btn {
  border-radius: 2px !important;
}

/* 主工作区：左侧编辑 + 右侧操作栏 */
.editor-workspace {
  flex: 1;
  min-height: 0;
  display: flex;
  overflow: hidden;
}

.editor-main {
  flex: 1;
  min-width: 0;
  height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 右侧独立操作区 */
.editor-action-panel {
  flex-shrink: 0;
  width: 132px;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  border-left: 1px solid #e4e7ed;
  box-sizing: border-box;
}

.action-panel-title {
  padding: 10px 12px 8px;
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  letter-spacing: 1px;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.action-panel-buttons {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 10px;
  overflow-y: auto;
}

.panel-btn {
  width: 100%;
  margin: 0 !important;
  padding: 10px 8px;
  height: auto;
  white-space: normal;
  line-height: 1.35;
}

.panel-btn :deep(.el-icon) {
  margin-right: 4px;
  vertical-align: middle;
}

/* TinyMCE 容器高度撑满 flex 父容器 */
.editor-main :deep(.tox-tinymce) {
  flex: 1 !important;
  min-height: 0 !important;
  border: none !important;
  border-radius: 0 !important;
}
</style>