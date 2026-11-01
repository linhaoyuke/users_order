<template>
  <TablePage
    title="用户管理"
    :data="users"
    :loading="loading"
    :total="total"
    @add="handleAdd"
    @search="handleSearch"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  >
    <el-table-column prop="id" label="ID" width="80" />
    <el-table-column prop="username" label="用户名" min-width="120" />
    <el-table-column prop="email" label="邮箱" min-width="180" />
    <el-table-column prop="full_name" label="姓名" min-width="120" />
    <el-table-column prop="phone" label="电话" min-width="120" />
    <el-table-column label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="row.is_active ? 'success' : 'danger'">
          {{ row.is_active ? '启用' : '禁用' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="角色" min-width="150">
      <template #default="{ row }">
        <div class="role-tags">
          <el-tag
            v-for="role in row.roles"
            :key="role.id"
            size="small"
            class="role-tag"
          >
            {{ role.name }}
          </el-tag>
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="创建时间" width="180">
      <template #default="{ row }">
        {{ formatDate(row.created_at) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="220" fixed="right">
      <template #default="{ row }">
        <div class="action-buttons">
          <el-button type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="warning" size="small" @click="handleAssignRoles(row)">
            分配角色
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </div>
      </template>
    </el-table-column>
  </TablePage>

  <!-- 用户表单对话框 -->
  <UserForm
    v-model="showUserForm"
    :user="currentUser"
    @success="handleFormSuccess"
  />



  <!-- 角色分配对话框 -->
  <RoleAssignDialog
    v-model="showRoleDialog"
    :user="currentUser"
    @success="handleRoleAssignSuccess"
  />
</template>

<script setup lang="ts">
import {onMounted, ref} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import TablePage from '@/components/TablePage.vue'
import UserForm from './components/UserForm.vue'
import RoleAssignDialog from './components/RoleAssignDialog.vue'
import {userApi} from '@/api/user'
import type {User} from '@/types/user'
import {formatDate} from '@/utils/date'

const users = ref<User[]>([])
const loading = ref(false)
const showUserForm = ref(false)
const showRoleDialog = ref(false)
const currentUser = ref<User | null>(null)

// 分页和搜索相关状态
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')

// 获取用户列表（核心逻辑重构）
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value
    }
    // 后端需要返回一个包含总数和结果的对象
    const response = await userApi.getUsers(params)
    // 假设后端返回 { count: number, results: User[] }
    users.value = response.data.results 
    total.value = response.data.count
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = (keyword: string) => {
  searchKeyword.value = keyword
  currentPage.value = 1 // 搜索时重置到第一页
  fetchUsers() // 重新从后端获取数据
}

// 分页大小改变
const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1 // 改变页面大小时重置到第一页
  fetchUsers()
}

// 当前页改变
const handleCurrentChange = (page: number) => {
  currentPage.value = page
  fetchUsers()
}

// 监听 pageSize 和 currentPage 的变化，自动重新获取数据
// watch([currentPage, pageSize], fetchUsers)

// 新增用户
const handleAdd = () => {
  currentUser.value = null
  showUserForm.value = true
}

// 编辑用户
const handleEdit = (user: User) => {
  currentUser.value = user
  showUserForm.value = true
}

// 删除用户
const handleDelete = async (user: User) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await userApi.deleteUser(user.id)
    ElMessage.success('删除成功')
    fetchUsers() // 重新加载当前页数据
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 分配角色
const handleAssignRoles = (user: User) => {
  currentUser.value = user
  showRoleDialog.value = true
}

// 表单提交成功
const handleFormSuccess = () => {
  fetchUsers() // 重新加载数据
}

// 角色分配成功
const handleRoleAssignSuccess = () => {
  fetchUsers() // 重新加载数据
}

onMounted(() => {
  fetchUsers()
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

/* 角色标签样式 */
.role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

.role-tag {
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
