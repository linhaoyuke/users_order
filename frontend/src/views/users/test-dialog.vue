<template>
  <div class="test-container">
    <h2>对话框测试</h2>
    <el-button type="primary" @click="showDialog = true">
      打开对话框
    </el-button>
    
    <el-dialog
      v-model="showDialog"
      title="测试对话框"
      width="500px"
    >
      <p>这是一个测试对话框</p>
      <template #footer>
        <el-button @click="showDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import {ref} from 'vue'

const showDialog = ref(false)
</script>

<style scoped>
.test-container {
  padding: 20px;
}
</style>
