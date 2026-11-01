<template>
  <div class="table-page">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h2>{{ title }}</h2>
      </div>
      
      <!-- 工具栏 -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <slot name="toolbar-left">
            <el-button type="primary" @click="handleAdd" v-if="showAdd">
              <el-icon><Plus /></el-icon>
              新增
            </el-button>
          </slot>
        </div>
        <div class="toolbar-right">
          <slot name="toolbar-right">
            <el-input
              v-model="searchKeyword"
              placeholder="请输入搜索关键词"
              style="width: 200px"
              clearable
              @input="(val: string) => searchKeyword = val"
              @clear="() => searchKeyword = ''"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </slot>
        </div>
      </div>
      
      <!-- 表格 -->
      <el-table
        :data="data"
        :loading="loading"
        stripe
        border
        style="width: 100%"
        class="custom-table"
        v-bind="$attrs"
      >
        <slot />
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container" v-if="showPagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref, watch} from 'vue'

interface Props {
  title: string
  data: any[]
  loading?: boolean
  showAdd?: boolean
  showPagination?: boolean
  total?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  showAdd: true,
  showPagination: true,
  total: 0
})

const emit = defineEmits<{
  add: []
  search: [keyword: string]
  'size-change': [size: number]
  'current-change': [page: number]
}>()

const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 使用 watch 来监听搜索关键词的变化，并加入长度判断和防抖
watch(searchKeyword, (newValue) => {
  // 只有当关键词为空或者长度大于等于2时，才触发搜索
  if (newValue === '' || newValue.length >= 2) {
    emit('search', newValue)
  }
})

const handleAdd = () => {
  emit('add')
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  emit('size-change', size)
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  emit('current-change', page)
}
</script>

<style scoped>
.table-page {
  height: 100%;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.table-toolbar {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 表格样式优化 */
.custom-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-table__header-wrapper) {
  background-color: #f8f9fa;
}

:deep(.el-table__header th) {
  background-color: #f8f9fa !important;
  color: #606266;
  font-weight: 600;
  border-bottom: 2px solid #e4e7ed;
}

:deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

:deep(.el-table td) {
  padding: 12px 0;
  vertical-align: middle;
}

:deep(.el-table__fixed-right) {
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .table-toolbar {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }

  /* 移动端表格优化 */
  :deep(.el-table td) {
    padding: 8px 0;
  }

  :deep(.el-table__fixed-right) {
    box-shadow: none;
  }
}
</style>
