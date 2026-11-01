<template>
  <el-dialog
    :model-value="modelValue"
    title="分配权限"
    width="600px"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <div v-if="role">
      <p>为角色 <strong>{{ role.name }}</strong> 分配权限：</p>
      
      <!-- 按资源分组显示权限 -->
      <div v-for="(perms, resource) in groupedPermissions" :key="resource" class="permission-group">
        <h4 class="resource-title">{{ resourceLabels[resource] || resource }}</h4>
        <el-checkbox-group v-model="selectedPermissionIds" class="permission-list">
          <el-checkbox
            v-for="permission in perms"
            :key="permission.id"
            :label="permission.id"
            class="permission-item"
          >
            <div class="permission-info">
              <div class="permission-name">{{ permission.name }}</div>
              <div class="permission-description">{{ permission.description }}</div>
            </div>
          </el-checkbox>
        </el-checkbox-group>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {computed, onMounted, ref, watch} from 'vue'
import {ElMessage} from 'element-plus'
import {roleApi} from '@/api/role'
import {permissionApi} from '@/api/permission'
import type {Permission, Role} from '@/types/auth'

interface Props {
  modelValue: boolean
  role?: Role | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const loading = ref(false)
const permissions = ref<Permission[]>([])
const selectedPermissionIds = ref<number[]>([])

const resourceLabels: Record<string, string> = {
  user: '用户管理',
  role: '角色管理',
  permission: '权限管理',
  order: '订单管理'
}

// 按资源分组权限
const groupedPermissions = computed(() => {
  const groups: Record<string, Permission[]> = {}
  permissions.value.forEach(permission => {
    if (!groups[permission.resource]) {
      groups[permission.resource] = []
    }
    groups[permission.resource].push(permission)
  })
  return groups
})

// 获取权限列表
const fetchPermissions = async () => {
  try {
    const response = await permissionApi.getPermissions()
    permissions.value = response.data
  } catch (error) {
    ElMessage.error('获取权限列表失败')
  }
}

// 监听角色变化
watch(() => props.role, (role) => {
  if (role && role.permissions) {
    selectedPermissionIds.value = role.permissions.map(permission => permission.id)
  } else {
    selectedPermissionIds.value = []
  }
}, { immediate: true })

const handleClose = () => {
  emit('update:modelValue', false)
  selectedPermissionIds.value = []
}

const handleSubmit = async () => {
  if (!props.role) return
  
  loading.value = true
  try {
    await roleApi.assignPermissions(props.role.id, selectedPermissionIds.value)
    ElMessage.success('权限分配成功')
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error('权限分配失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPermissions()
})
</script>

<style scoped>
.permission-group {
  margin-bottom: 24px;
}

.resource-title {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 8px;
}

.permission-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding-left: 16px;
}

.permission-item {
  width: 100%;
  margin-right: 0;
}

.permission-info {
  margin-left: 8px;
}

.permission-name {
  font-weight: 500;
  color: #303133;
}

.permission-description {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
