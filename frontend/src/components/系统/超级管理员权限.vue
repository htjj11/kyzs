<template>
  <div class="super-admin-container">
    <el-alert
      type="warning"
      :closable="false"
      show-icon
      title="超级管理员"
      description="当前账号已具备 admin:admin 权限，可在此进行系统级管理操作。"
      style="margin-bottom: 16px;"
    />
    <el-tabs v-model="activeTab">
      <el-tab-pane label="用户权限管理" name="user_permission">
        <UserPermissionManager />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import UserPermissionManager from './超级管理员权限/用户权限管理.vue'

const activeTab = ref('user_permission')
</script>

<style scoped>
.super-admin-container {
  padding: 4px 0;
}
</style>
