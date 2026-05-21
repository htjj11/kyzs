<template>
  <div class="chat-container">
    <iframe :src="ragflow_url" style="width: 100%; height: 100%; min-height: 600px" frameborder="0">
    </iframe>
  </div>
</template>

<script setup>
import { ragflow_url } from '@/api/config.js'
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  min-height: 600px;
}
</style>
