<template>
  <div class="settings-container">
    <h1>其他设置</h1>
    <!-- 内容区域 -->
    <div class="settings-content">
      <el-tabs v-model="activeTab" type="card" style="height: 100%;">
        <el-tab-pane label="格式设置" name="format">
          <div class="tab-content">
            <setting_format></setting_format>
          </div>
        </el-tab-pane>
        <el-tab-pane label="标签设置" name="label">
          <div class="tab-content">
            <setting_label></setting_label>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>



<script setup>
import { ref } from 'vue';
import setting_format from './small/setting_format.vue';
import setting_label from './small/setting_label.vue';

// 创建响应式状态控制显示/隐藏
const isFormatVisible = ref(false);
const isLabelVisible = ref(false);

// 切换显示状态的函数
function toggleFormatVisibility() {
  isFormatVisible.value = !isFormatVisible.value;
}
function toggleLabelVisibility() {
  isLabelVisible.value = !isLabelVisible.value;
}
</script>

<style scoped>
.settings-container {
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.settings-content {
  flex: 1;
  margin-top: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.el-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.el-tabs__content {
  flex: 1;
  padding: 0;
  overflow: hidden;
}

.tab-content {
  height: 100%;
  overflow: auto;
}

/* 调整选项卡样式 */
.el-tabs--card .el-tabs__header {
  border-bottom: 1px solid #ebeef5;
}

.el-tabs--card .el-tabs__nav {
  padding: 0;
}

.el-tabs--card .el-tabs__nav-wrap::after {
  display: none;
}
</style>
