<template>
  <div class="chat-container">
    <!-- 头部标题 -->
    <div class="chat-header">
      <h2>大模型知识库问答</h2>
    </div>

    <!-- 对话内容区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 历史对话 -->
      <div v-for="message in chatHistory" :key="message.id" :class="['message', message.role]">
        <div class="message-avatar">{{ message.role === 'user' ? '用户' : 'AI' }}</div>
        <div class="message-content">
          <div class="message-text" v-html="message.content"></div>
          <div class="message-time">{{ message.time }}</div>
        </div>
      </div>
      <!-- 正在输入提示 -->
      <div v-if="isTyping" class="message ai">
        <div class="message-avatar">AI</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-area">
      <div class="input-wrapper">
        <textarea
          v-model="userInput"
          @keydown.ctrl.enter="sendMessage"
          @keydown.alt.enter="insertNewLine"
          placeholder="请输入您的问题"
          :disabled="isTyping"
          rows="1"
          ref="textArea"
        ></textarea>
        <div class="input-actions">
          <el-button
            type="primary"
            @click="sendMessage"
            :disabled="!userInput.trim() || isTyping"
            size="default"
            class="send-button"
          >
            发送
          </el-button>
        </div>
      </div>
      <div class="input-tips">
        <span>提示：按 Ctrl+Enter 发送消息，按 Alt+Enter 换行</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import api from '@/api/request';
import * as marked from 'marked'; // 引入 marked 库用于 Markdown 渲染

// 定义消息类型
interface ChatMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  time: string;
}

// 聊天历史记录
const chatHistory = ref<ChatMessage[]>([]);
// 用户输入内容
const userInput = ref('');
// 是否正在输入（AI响应中）
const isTyping = ref(false);
// 消息容器引用
const messagesContainer = ref<HTMLDivElement>();
// 文本区域引用
const textArea = ref<HTMLTextAreaElement>();

// 初始化时加载模拟历史记录
onMounted(() => {
  // 模拟历史消息数据
  const mockHistory: ChatMessage[] = [
    {
      id: '1',
      role: 'user',
      content: '怎么使用大模型知识问答？',
      time: '14:30:25'
    },
    {
      id: '2',
      role: 'ai',
      content: '从下方点击输入就可以了',
      time: '14:30:40'
    }
  ];
  
  chatHistory.value = mockHistory;
  
  // 自动调整文本框高度
  adjustTextareaHeight();
  
  // 滚动到底部
  nextTick(() => {
    scrollToBottom();
  });
});

// 自动调整文本框高度
const adjustTextareaHeight = () => {
  if (textArea.value) {
    textArea.value.style.height = 'auto';
    const scrollHeight = textArea.value.scrollHeight;
    // 限制最大高度为150px
    textArea.value.style.height = Math.min(scrollHeight, 150) + 'px';
  }
};

// 插入新行（Alt+Enter）
const insertNewLine = (event: KeyboardEvent) => {
  event.preventDefault();
  const start = (event.target as HTMLTextAreaElement).selectionStart;
  const end = (event.target as HTMLTextAreaElement).selectionEnd;
  userInput.value = userInput.value.substring(0, start) + '\n' + userInput.value.substring(end);
  
  // 调整高度并重新聚焦
  nextTick(() => {
    adjustTextareaHeight();
    const textarea = textArea.value;
    if (textarea) {
      textarea.focus();
      textarea.setSelectionRange(start + 1, start + 1);
    }
  });
};

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

// 格式化时间
const formatTime = () => {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};

// 发送消息
const sendMessage = async () => {
  const message = userInput.value.trim();
  if (!message || isTyping.value) return;

  // 添加用户消息到聊天历史
  const userMessage: ChatMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: message,
    time: formatTime()
  };
  chatHistory.value.push(userMessage);

  // 清空输入框并调整高度
  userInput.value = '';
  adjustTextareaHeight();

  // 滚动到底部
  await nextTick();
  scrollToBottom();

  // 设置为正在输入状态
  isTyping.value = true;

  try {
    // 创建AI回复消息对象
    const aiMessageId = (Date.now() + 1).toString();
    const aiMessage: ChatMessage = {
      id: aiMessageId,
      role: 'ai',
      content: '',
      time: formatTime()
    };
    
    // 初始化AI回复消息
    chatHistory.value.push(aiMessage);
    
    // 调用流式API
    await callStreamChatApi(message, aiMessageId);
    
  } catch (error) {
    console.error('发送消息失败:', error);
    ElMessage.error('发送消息失败，请稍后重试');
  } finally {
    // 完成输入状态
    isTyping.value = false;
  }
};

// 调用流式对话接口
const callStreamChatApi = async (message, aiMessageId) => {
  try {
    // 使用Fetch API处理流式响应
    const response = await fetch('http://10.68.202.238:8000/llm/stream_chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('无法获取响应流');
    }

    const decoder = new TextDecoder();
    let done = false;
    let currentText = '';
    let hasHtmlContent = false;

    while (!done && !hasHtmlContent) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;
      
      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        
        // 检查是否包含HTML标签
        if (chunk.includes('<html') || chunk.includes('<!DOCTYPE')) {
          hasHtmlContent = true;
          break;
        }
        
        // 分割多个JSON响应
        const lines = chunk.split(/\r?\n/);
        
        for (const line of lines) {
          if (line.trim() === 'Connection closed' || line.trim() === '') {
            continue;
          }
          console.log('原始行:', line);
          
          try {
            // 去除data:前缀
            let jsonStr = line.trim();
            if (jsonStr.startsWith('data: ')) {
              jsonStr = jsonStr.substring(5);
            }
            
            // 再次检查是否包含HTML标签
            if (jsonStr.includes('<html') || jsonStr.includes('<!DOCTYPE')) {
              hasHtmlContent = true;
              break;
            }
            
            // 尝试解析JSON
            const data = JSON.parse(jsonStr);
            
            // 提取文本内容
            if (data.type === 'textResponseChunk' && data.textResponse) {
              currentText += data.textResponse;
              
              // 更新AI回复消息
              const aiMessageIndex = chatHistory.value.findIndex(msg => msg.id === aiMessageId);
              if (aiMessageIndex !== -1) {
                // 使用 marked 库将 Markdown 文本转换为 HTML
                chatHistory.value[aiMessageIndex].content = marked.parse(currentText);
                chatHistory.value[aiMessageIndex].time = formatTime();
              }
              
              // 滚动到底部
              await nextTick();
              scrollToBottom();
            }
            
            // 检查是否结束并且有sources信息
            if (data.close && data.sources && data.sources.length > 0) {
              // 处理sources信息并附加到消息末尾
              let sourcesHtml = '<br><br><div class="sources-info"><h4>参考资料：</h4>';
              
              data.sources.forEach((source: any, index: number) => {
                if (source.title || source.text) {
                  sourcesHtml += `<div class="source-item">`;
                  
                  // 添加标题
                  if (source.title) {
                    sourcesHtml += `<div class="source-title"><strong>来源 ${index + 1}：</strong>${source.title}</div>`;
                  }
                  
                  // 添加文本内容
                  if (source.text) {
                    // 清理文本内容中的元数据信息
                    let cleanText = source.text;
                    if (cleanText.includes('<document_metadata>')) {
                      cleanText = cleanText.replace(/<document_metadata>[\s\S]*?<\/document_metadata>/, '');
                    }
                    cleanText = cleanText.trim();
                    
                    if (cleanText) {
                      sourcesHtml += `<div class="source-text">${cleanText}</div>`;
                    }
                  }
                  
                  sourcesHtml += `</div>`;
                }
              });
              
              sourcesHtml += '</div>';
              
              // 更新AI回复消息，添加sources信息
              const aiMessageIndex = chatHistory.value.findIndex(msg => msg.id === aiMessageId);
              if (aiMessageIndex !== -1) {
                // 使用 marked 库将 Markdown 文本转换为 HTML，然后添加参考资料
                chatHistory.value[aiMessageIndex].content = marked.parse(currentText) + sourcesHtml;
                chatHistory.value[aiMessageIndex].time = formatTime();
              }
              
              // 滚动到底部
              await nextTick();
              scrollToBottom();
              
              done = true;
              break;
            }
            
            // 普通结束检查
            if (data.close && (!data.sources || data.sources.length === 0)) {
              // 使用 marked 库将 Markdown 文本转换为 HTML
              const aiMessageIndex = chatHistory.value.findIndex(msg => msg.id === aiMessageId);
              if (aiMessageIndex !== -1) {
                chatHistory.value[aiMessageIndex].content = marked.parse(currentText);
                chatHistory.value[aiMessageIndex].time = formatTime();
              }
              done = true;
              break;
            }
          } catch (e) {
            console.warn('解析JSON失败:', e);
          }
        }
      }
    }

    // 如果检测到HTML内容，显示错误信息
    if (hasHtmlContent) {
      const aiMessageIndex = chatHistory.value.findIndex(msg => msg.id === aiMessageId);
      if (aiMessageIndex !== -1) {
        chatHistory.value[aiMessageIndex].content = '抱歉，服务器返回了无效响应，请稍后重试。';
        chatHistory.value[aiMessageIndex].time = formatTime();
      }
      ElMessage.error('服务器返回了无效响应，请稍后重试');
    }

  } catch (error) {
    console.error('流式请求失败:', error);
    
    // 更新AI消息显示错误
    const aiMessageIndex = chatHistory.value.findIndex(msg => msg.id === aiMessageId);
    if (aiMessageIndex !== -1) {
      chatHistory.value[aiMessageIndex].content = '抱歉，处理您的请求时发生错误，请稍后重试。';
      chatHistory.value[aiMessageIndex].time = formatTime();
    }
    
    ElMessage.error('获取响应失败，请稍后重试');
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  background: #ffffff;
  color: #303133;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e4e7ed;
}

.chat-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f8f9fa;
}

.message {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message.user {
  justify-content: flex-end;
}

.message.ai {
  justify-content: flex-start;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: white;
  margin: 0 12px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background-color: #409eff;
  order: 2;
}

.message.ai .message-avatar {
  background-color: #67c23a;
  order: 1;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message.user .message-content {
  align-items: flex-end;
  order: 1;
}

.message.ai .message-content {
  align-items: flex-start;
  order: 2;
}

.message-text {
  padding: 12px 16px;
  border-radius: 18px;
  word-wrap: break-word;
  line-height: 1.6;
}

.message.user .message-text {
  background-color: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.ai .message-text {
  background-color: #ffffff;
  color: #333333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 12px;
  color: #666666;
  margin-top: 4px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #999999;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  30% {
    transform: scale(1);
    opacity: 1;
  }
}

.chat-input-area {
  padding: 20px;
  background-color: #ffffff;
  border-top: 1px solid #e0e0e0;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

textarea {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  resize: none;
  transition: border-color 0.3s;
  font-family: inherit;
  min-height: 48px;
}

textarea:focus {
  outline: none;
  border-color: #667eea;
}

textarea:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.send-button {
  padding: 12px 24px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background-color: #337ecc;
}

.send-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.input-tips {
  margin-top: 8px;
  font-size: 12px;
  color: #999999;
  text-align: left;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    height: 100vh;
    border-radius: 0;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .chat-header h2 {
    font-size: 20px;
  }
  
  .chat-messages,
  .chat-input-area {
    padding: 16px;
  }
}

/* 参考资料样式 */
.sources-info {
  margin-top: 16px;
  padding: 12px;
  background-color: #f0f7ff;
  border-radius: 8px;
  border: 1px solid #d9e8ff;
}

.sources-info h4 {
  margin: 0 0 12px 0;
  color: #1890ff;
  font-size: 14px;
}

.source-item {
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #91d5ff;
}

.source-item:last-child {
  margin-bottom: 0;
}

.source-title {
  font-size: 13px;
  color: #262626;
  margin-bottom: 4px;
  font-weight: 500;
}

/* 增加选择器特异性以确保样式生效 */
.message.ai .message-text .sources-info .source-item .source-text {
  font-size: 11px !important; /* 字体小一号，添加!important确保优先级 */
  color: #ff0000 !important; /* 红色字体以明显验证样式变化 */
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.source-text:empty {
  display: none;
}
</style>