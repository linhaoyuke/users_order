<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>
      
      <el-form
        ref="profileFormRef"
        :model="profileForm"
        :rules="profileRules"
        label-width="100px"
        class="profile-form"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名" prop="username">
              <el-input
                v-model="profileForm.username"
                disabled
                placeholder="用户名不可修改"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="姓名" prop="full_name">
              <el-input
                v-model="profileForm.full_name"
                placeholder="请输入姓名"
                :disabled="!isEditing"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input
                v-model="profileForm.email"
                placeholder="请输入邮箱"
                :disabled="!isEditing"
              />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="profileForm.phone"
                placeholder="请输入手机号"
                :disabled="!isEditing"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-tag :type="profileForm.is_active ? 'success' : 'danger'">
                {{ profileForm.is_active ? '激活' : '禁用' }}
              </el-tag>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="角色">
              <div class="role-tags">
                <el-tag
                  v-for="role in profileForm.roles"
                  :key="role.id"
                  type="info"
                  class="role-tag"
                >
                  {{ role.name }}
                </el-tag>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button
            v-if="!isEditing"
            type="primary"
            @click="startEdit"
          >
            编辑信息
          </el-button>
          
          <template v-else>
            <el-button
              type="primary"
              :loading="loading"
              @click="saveProfile"
            >
              保存
            </el-button>
            <el-button @click="cancelEdit">
              取消
            </el-button>
          </template>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import {onMounted, reactive, ref} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'
import {userApi} from '@/api/user'
import type {User} from '@/types/user'

const profileFormRef = ref<FormInstance>()
const loading = ref(false)
const isEditing = ref(false)

const profileForm = reactive<Partial<User>>({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  is_active: true,
  roles: []
})

const originalData = ref<Partial<User>>({})

const profileRules: FormRules = {
  full_name: [
    { max: 50, message: '姓名长度不能超过50个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ]
}

// 获取用户信息
const fetchProfile = async () => {
  loading.value = true
  try {
    const response = await userApi.getCurrentUserProfile()
    const userData = response.data
    
    Object.assign(profileForm, userData)
    originalData.value = { ...userData }
  } catch (error) {
    ElMessage.error('获取个人信息失败')
  } finally {
    loading.value = false
  }
}

// 开始编辑
const startEdit = () => {
  isEditing.value = true
  originalData.value = { ...profileForm }
}

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false
  Object.assign(profileForm, originalData.value)
}

// 保存信息
const saveProfile = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const updateData = {
          full_name: profileForm.full_name,
          email: profileForm.email,
          phone: profileForm.phone
        }
        
        const response = await userApi.updateCurrentUserProfile(updateData)
        Object.assign(profileForm, response.data)
        originalData.value = { ...response.data }
        
        isEditing.value = false
        ElMessage.success('个人信息更新成功')
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '更新失败')
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.profile-form {
  margin-top: 20px;
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
</style>
