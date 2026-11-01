<template>
  <el-dialog
    :model-value="modelValue"
    title="分配角色"
    width="500px"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <div v-if="user">
      <p>为用户 <strong>{{ user.username }}</strong> 分配角色：</p>
      
      <el-checkbox-group v-model="selectedRoleIds" class="role-list">
        <el-checkbox
          v-for="role in roles"
          :key="role.id"
          :label="role.id"
          class="role-item"
        >
          <div class="role-info">
            <div class="role-name">{{ role.name }}</div>
            <div class="role-description">{{ role.description }}</div>
          </div>
        </el-checkbox>
      </el-checkbox-group>
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
import {onMounted, ref, watch} from 'vue'
import {ElMessage} from 'element-plus'
import {userApi} from '@/api/user'
import {roleApi} from '@/api/role'
import type {User} from '@/types/user'
import type {Role} from '@/types/auth'

interface Props {
  modelValue: boolean
  user?: User | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const loading = ref(false)
const roles = ref<Role[]>([])
const selectedRoleIds = ref<number[]>([])

// 获取角色列表
const fetchRoles = async () => {
  try {
    const response = await roleApi.getRoles()
    roles.value = response.data
  } catch (error) {
    ElMessage.error('获取角色列表失败')
  }
}

// 监听用户变化
watch(() => props.user, (user) => {
  if (user) {
    selectedRoleIds.value = user.roles.map(role => role.id)
  } else {
    selectedRoleIds.value = []
  }
}, { immediate: true })

const handleClose = () => {
  emit('update:modelValue', false)
  selectedRoleIds.value = []
}

const handleSubmit = async () => {
  if (!props.user) return
  
  loading.value = true
  try {
    await userApi.assignRoles(props.user.id, selectedRoleIds.value)
    ElMessage.success('角色分配成功')
    emit('success')
    handleClose()
  } catch (error) {
    ElMessage.error('角色分配失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRoles()
})
</script>

<style scoped>
.role-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.role-item {
  width: 100%;
  margin-right: 0;
}

.role-info {
  margin-left: 8px;
}

.role-name {
  font-weight: 500;
  color: #303133;
}

.role-description {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
