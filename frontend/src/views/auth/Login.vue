<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>后台管理系统</h2>
        <p>请输入您的账号和密码</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item prop="captcha">
          <div class="captcha-container">
            <el-input
              v-model="loginForm.captcha"
              placeholder="请输入计算结果"
              size="large"
              prefix-icon="ChatDotSquare"
              style="flex: 1;"
            />
            <div class="captcha-image-container" @click="refreshCaptcha">
              <img v-if="captchaImage" :src="captchaImage" alt="Captcha" class="captcha-image"/>
              <div v-else class="captcha-loading">加载中...</div>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="authStore.loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <!-- <p>默认管理员账号：admin / admin123</p> -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {onMounted, reactive, ref} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import {useAuthStore} from '@/stores/auth'
import type {LoginForm} from '@/types/auth'
import {getCaptcha} from '@/api/auth'

const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const captchaImage = ref<string>('')

const loginForm = reactive<LoginForm>({
  username: '',
  password: '',
  captcha: '',
  captcha_token: '' // 新增 token 字段
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入计算结果', trigger: 'blur' },
    { pattern: /^\d+$/, message: '请输入正确的数字', trigger: 'blur' }
  ]
}

// 获取验证码
const refreshCaptcha = async () => {
  try {
    const response = await getCaptcha()
    captchaImage.value = response.data.image
    loginForm.captcha_token = response.data.token // 保存 token
  } catch (error) {
    console.error('获取验证码失败:', error)
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      const success = await authStore.login(loginForm)
      if (success) {
        // 使用 window.location.href 进行强制页面刷新和跳转
        // 这可以绕过因响应式状态更新不及时导致的路由守卫问题
        window.location.href = '/'
      } else {
        // 登录失败后刷新验证码
        refreshCaptcha()
        loginForm.captcha = ''
      }
    }
  })
}

// 页面加载时获取验证码
onMounted(() => {
  refreshCaptcha()
})
</script>

<style scoped>
.login-container {
  height: 100vh;
  background-image: url('../../../1.jpeg');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  color: #333;
  margin-bottom: 10px;
  font-weight: 600;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
}

.login-footer {
  text-align: center;
  color: #999;
  font-size: 12px;
}

.login-footer p {
  margin: 0;
}

.captcha-container {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.captcha-image-container {
  width: 120px; /* 匹配后端宽度 */
  height: 40px; /* 匹配输入框高度 */
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  transition: border-color 0.3s;
}

.captcha-image-container:hover {
  border-color: #409eff;
}

.captcha-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.captcha-loading {
  font-size: 12px;
  color: #909399;
}
</style>