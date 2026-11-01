<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑权限' : '新增权限'"
    width="600px"
    :append-to-body="true"
    :destroy-on-close="true"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="80px"
    >
      <el-form-item label="权限名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入权限名称" />
      </el-form-item>
      
      <el-form-item label="权限编码" prop="code">
        <el-input v-model="form.code" placeholder="请输入权限编码" />
      </el-form-item>
      
      <el-form-item label="资源" prop="resource">
        <el-select v-model="form.resource" placeholder="请选择资源" style="width: 100%">
          <el-option label="用户管理" value="user" />
          <el-option label="角色管理" value="role" />
          <el-option label="权限管理" value="permission" />
          <el-option label="订单管理" value="order" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="操作" prop="action">
        <el-select v-model="form.action" placeholder="请选择操作" style="width: 100%">
          <el-option label="创建" value="create" />
          <el-option label="查看" value="read" />
          <el-option label="更新" value="update" />
          <el-option label="删除" value="delete" />
        </el-select>
      </el-form-item>
      
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="请输入权限描述"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import {computed, reactive, ref, watch} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'
import {type CreatePermissionForm, permissionApi, type UpdatePermissionForm} from '@/api/permission'
import type {Permission} from '@/types/auth'

interface Props {
  modelValue: boolean
  permission?: Permission | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const isEdit = computed(() => !!props.permission)

const form = reactive<CreatePermissionForm & UpdatePermissionForm>({
  name: '',
  code: '',
  resource: '',
  action: '',
  description: ''
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入权限名称', trigger: 'blur' },
    { min: 2, max: 50, message: '权限名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入权限编码', trigger: 'blur' },
    { min: 2, max: 50, message: '权限编码长度在 2 到 50 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_:]*$/, message: '权限编码只能包含字母、数字、下划线和冒号，且不能以数字开头', trigger: 'blur' }
  ],
  resource: [
    { required: true, message: '请选择资源', trigger: 'change' }
  ],
  action: [
    { required: true, message: '请选择操作', trigger: 'change' }
  ]
}

// 先定义resetForm函数
const resetForm = () => {
  form.name = ''
  form.code = ''
  form.resource = ''
  form.action = ''
  form.description = ''
}

// 监听权限数据变化
watch(() => props.permission, (permission) => {
  if (permission) {
    form.name = permission.name
    form.code = permission.code
    form.resource = permission.resource
    form.action = permission.action
    form.description = permission.description || ''
  } else {
    resetForm()
  }
}, { immediate: true })

const handleClose = () => {
  emit('update:modelValue', false)
  resetForm()
  formRef.value?.clearValidate()
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isEdit.value && props.permission) {
          await permissionApi.updatePermission(props.permission.id, form)
          ElMessage.success('更新成功')
        } else {
          await permissionApi.createPermission(form)
          ElMessage.success('创建成功')
        }
        emit('success')
        handleClose()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>
