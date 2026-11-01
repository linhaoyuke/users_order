<template>
  <TablePage
    title="权限管理"
    :data="paginatedPermissions"
    :loading="loading"
    :total="total"
    @add="handleAdd"
    @search="handleSearch"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="name" label="权限名称" min-width="120" />
    <el-table-column prop="code" label="权限编码" min-width="150" />
    <el-table-column prop="resource" label="资源" width="120">
      <template #default="{ row }">
        <el-tag type="info">{{ resourceLabels[row.resource] || row.resource }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="action" label="操作" width="100">
      <template #default="{ row }">
        <el-tag :type="actionTagType(row.action)">{{ actionLabels[row.action] || row.action }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="description" label="描述" min-width="200" />
    <el-table-column label="操作" width="160" fixed="right">
      <template #default="{ row }">
        <div class="action-buttons">
          <el-button type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </div>
      </template>
    </el-table-column>
  </TablePage>

  <!-- 权限表单对话框 -->
  <PermissionForm
    v-model="showPermissionForm"
    :permission="currentPermission"
    @success="handleFormSuccess"
  />
</template>

<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import TablePage from '@/components/TablePage.vue'
import PermissionForm from './components/PermissionForm.vue'
import {permissionApi} from '@/api/permission'
import type {Permission} from '@/types/auth'

const permissions = ref<Permission[]>([])
const loading = ref(false)
const showPermissionForm = ref(false)
const currentPermission = ref<Permission | null>(null)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')

const resourceLabels: Record<string, string> = {
  user: '用户管理',
  role: '角色管理',
  permission: '权限管理',
  order: '订单管理'
}

const actionLabels: Record<string, string> = {
  create: '创建',
  read: '查看',
  update: '更新',
  delete: '删除'
}

const actionTagType = (action: string) => {
  const types: Record<string, string> = {
    create: 'success',
    read: 'info',
    update: 'warning',
    delete: 'danger'
  }
  return types[action] || 'info'
}

// 过滤和分页后的权限列表
const filteredPermissions = computed(() => {
  if (!searchKeyword.value) {
    return permissions.value
  }
  return permissions.value.filter(permission =>
    permission.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    permission.code.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    permission.resource.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    permission.action.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    (permission.description && permission.description.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  )
})

const paginatedPermissions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPermissions.value.slice(start, end)
})

// 更新总数
const updateTotal = () => {
  total.value = filteredPermissions.value.length
}

// 获取权限列表
const fetchPermissions = async () => {
  loading.value = true
  try {
    const response = await permissionApi.getPermissions()
    permissions.value = response.data
    updateTotal()
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  } finally {
    loading.value = false
  }
}

// 新增权限
const handleAdd = () => {
  currentPermission.value = null
  showPermissionForm.value = true
}

// 编辑权限
const handleEdit = (permission: Permission) => {
  currentPermission.value = permission
  showPermissionForm.value = true
}

// 删除权限
const handleDelete = async (permission: Permission) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除权限 "${permission.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await permissionApi.deletePermission(permission.id)
    ElMessage.success('删除成功')
    fetchPermissions()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 搜索
const handleSearch = (keyword: string) => {
  searchKeyword.value = keyword
  currentPage.value = 1 // 搜索时重置到第一页
  updateTotal()
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1 // 改变页面大小时重置到第一页
}

// 当前页改变
const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 表单提交成功
const handleFormSuccess = () => {
  fetchPermissions()
}

onMounted(() => {
  fetchPermissions()
})
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.action-buttons .el-button {
  margin: 0;
}

/* 响应式处理 */
@media (max-width: 1200px) {
  .action-buttons {
    flex-direction: column;
    gap: 4px;
    align-items: stretch;
  }

  .action-buttons .el-button {
    width: 100%;
    min-width: auto;
  }
}
</style>
