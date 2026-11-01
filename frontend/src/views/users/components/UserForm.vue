<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑用户' : '新增用户'"
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
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      
      <el-form-item label="密码" prop="password" v-if="!isEdit">
        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          show-password
        />
      </el-form-item>
      
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" placeholder="请输入邮箱" />
      </el-form-item>
      
      <el-form-item label="姓名" prop="full_name">
        <el-input v-model="form.full_name" placeholder="请输入姓名" />
      </el-form-item>
      
      <el-form-item label="电话" prop="phone">
        <el-input v-model="form.phone" placeholder="请输入电话" />
      </el-form-item>
      
      <el-form-item label="状态" prop="is_active">
        <el-switch v-model="form.is_active" />
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
import {userApi} from '@/api/user'
import type {CreateUserForm, UpdateUserForm, User} from '@/types/user'

interface Props {
  modelValue: boolean
  user?: User | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()



const formRef = ref<FormInstance>()
const loading = ref(false)

const isEdit = computed(() => !!props.user)

const form = reactive<CreateUserForm & UpdateUserForm>({
  username: '',
  password: '',
  email: '',
  full_name: '',
  phone: '',
  is_active: true
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 先定义resetForm函数
const resetForm = () => {
  form.username = ''
  form.password = ''
  form.email = ''
  form.full_name = ''
  form.phone = ''
  form.is_active = true
}

// 监听用户数据变化
watch(() => props.user, (user) => {
  if (user) {
    form.username = user.username
    form.email = user.email
    form.full_name = user.full_name || ''
    form.phone = user.phone || ''
    form.is_active = user.is_active
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
        if (isEdit.value && props.user) {
          await userApi.updateUser(props.user.id, form)
          ElMessage.success('更新成功')
        } else {
          await userApi.createUser(form)
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
