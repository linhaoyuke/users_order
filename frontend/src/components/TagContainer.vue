<template>
  <div class="tag-container">
    <slot />
    <span v-if="showEmpty && isEmpty" class="empty-text">
      {{ emptyText }}
    </span>
  </div>
</template>

<script setup lang="ts">
import {computed, useSlots} from 'vue'

interface Props {
  showEmpty?: boolean
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  showEmpty: false,
  emptyText: '暂无数据'
})

const slots = useSlots()

// 检查是否为空
const isEmpty = computed(() => {
  return !slots.default || !slots.default().length
})
</script>

<style scoped>
.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
  min-height: 24px; /* 确保即使没有内容也有最小高度 */
}

.tag-container :deep(.el-tag) {
  margin: 0;
  white-space: nowrap;
}

.empty-text {
  color: #909399;
  font-style: italic;
  font-size: 12px;
}

/* 响应式处理 */
@media (max-width: 768px) {
  .tag-container {
    gap: 2px;
  }
  
  .tag-container :deep(.el-tag) {
    font-size: 11px;
    padding: 2px 6px;
  }
}
</style>
