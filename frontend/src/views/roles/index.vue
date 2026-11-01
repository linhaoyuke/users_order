<template>
  <TablePage
    title="角色管理"
    :data="paginatedRoles"
    :loading="loading"
    :total="total"
    @add="handleAdd"
    @search="handleSearch"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="name" label="角色名称" min-width="120" />
    <el-table-column prop="code" label="角色编码" min-width="120" />
    <el-table-column prop="description" label="描述" min-width="200" />
    <el-table-column label="权限" min-width="300">
      <template #default="{ row }">
        <div class="permission-tags">
          <el-tag
            v-for="permission in row.permissions"
            :key="permission.id"
            size="small"
            class="permission-tag"
          >
            {{ permission.name }}
          </el-tag>
          <span v-if="!row.permissions || row.permissions.length === 0" class="text-gray">
            暂无权限
          </span>
        </div>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="260" fixed="right">
      <template #default="{ row }">
        <div class="action-buttons">
          <el-button type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="warning" size="small" @click="handleAssignPermissions(row)">
            分配权限
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </div>
      </template>
    </el-table-column>
  </TablePage>

  <!-- 角色表单对话框 -->
  <RoleForm
    v-model="showRoleForm"
    :role="currentRole"
    @success="handleFormSuccess"
  />

  <!-- 权限分配对话框 -->
  <PermissionAssignDialog
    v-model="showPermissionDialog"
    :role="currentRole"
    @success="handlePermissionAssignSuccess"
  />
</template>

<script setup lang="ts">
import {computed, onMounted, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import TablePage from '@/components/TablePage.vue'
import RoleForm from './components/RoleForm.vue'
import PermissionAssignDialog from './components/PermissionAssignDialog.vue'
import {roleApi} from '@/api/role'
import type {Role} from '@/types/auth'

const roles = ref<Role[]>([])
const loading = ref(false)
const showRoleForm = ref(false)
const showPermissionDialog = ref(false)
const currentRole = ref<Role | null>(null)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')

// 过滤和分页后的角色列表
const filteredRoles = computed(() => {
  if (!searchKeyword.value) {
    return roles.value
  }
  return roles.value.filter(role =>
    role.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    role.code.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
    (role.description && role.description.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  )
})

const paginatedRoles = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRoles.value.slice(start, end)
})

// 更新总数
const updateTotal = () => {
  total.value = filteredRoles.value.length
}

// 获取角色列表
const fetchRoles = async () => {
  loading.value = true
  try {
    const response = await roleApi.getRoles()
    roles.value = response.data
    updateTotal()
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

// 新增角色
const handleAdd = () => {
  currentRole.value = null
  showRoleForm.value = true
}

// 编辑角色
const handleEdit = (role: Role) => {
  currentRole.value = role
  showRoleForm.value = true
}

// 删除角色
const handleDelete = async (role: Role) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除角色 "${role.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await roleApi.deleteRole(role.id)
    ElMessage.success('删除成功')
    fetchRoles()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 分配权限
const handleAssignPermissions = (role: Role) => {
  currentRole.value = role
  showPermissionDialog.value = true
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
  fetchRoles()
}

// 权限分配成功
const handlePermissionAssignSuccess = () => {
  fetchRoles()
}

onMounted(() => {
  fetchRoles()
})
</script>

<style scoped>
.text-gray {
  color: #909399;
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.action-buttons .el-button {
  margin: 0;
}

/* 权限标签样式 */
.permission-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.permission-tag {
  margin: 0;
  white-space: nowrap;
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
