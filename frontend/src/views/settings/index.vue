<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>系统设置</span>
        </div>
      </template>
      
      <el-tabs 
        v-model="activeTab" 
        class="settings-tabs"
        :class="`theme-${currentThemeType}`"
        :style="{ '--el-color-primary': primaryColor }"
      >
        <!-- 修改密码 -->
        <el-tab-pane label="修改密码" name="password">
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="120px"
            class="settings-form"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                placeholder="请输入当前密码"
                show-password
                autocomplete="current-password"
              />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="请输入新密码"
                show-password
                autocomplete="new-password"
              />
            </el-form-item>

            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                placeholder="请再次输入新密码"
                show-password
                autocomplete="new-password"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="passwordLoading"
                @click="changePassword"
              >
                修改密码
              </el-button>
              <el-button @click="resetPasswordForm">
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 个人信息 -->
        <el-tab-pane label="个人信息" name="profile">
          <div class="profile-settings">
            <!-- 修改邮箱 -->
            <div class="setting-section">
              <h3 class="section-title">修改邮箱</h3>
              <el-form
                ref="emailFormRef"
                :model="emailForm"
                :rules="emailRules"
                label-width="120px"
                class="settings-form"
              >
                <el-form-item label="当前邮箱">
                  <el-input
                    :model-value="currentUserInfo.email"
                    disabled
                    placeholder="当前邮箱"
                  />
                </el-form-item>

                <el-form-item label="新邮箱" prop="new_email">
                  <el-input
                    v-model="emailForm.new_email"
                    placeholder="请输入新邮箱"
                    type="email"
                  />
                </el-form-item>

                <el-form-item label="确认新邮箱" prop="confirm_email">
                  <el-input
                    v-model="emailForm.confirm_email"
                    placeholder="请再次输入新邮箱"
                    type="email"
                  />
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    :loading="emailLoading"
                    @click="changeEmail"
                  >
                    修改邮箱
                  </el-button>
                  <el-button @click="resetEmailForm">
                    重置
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <!-- 分隔线 -->
            <el-divider />

            <!-- 修改手机号 -->
            <div class="setting-section">
              <h3 class="section-title">修改手机号</h3>
              <el-form
                ref="phoneFormRef"
                :model="phoneForm"
                :rules="phoneRules"
                label-width="120px"
                class="settings-form"
              >
                <el-form-item label="当前手机号">
                  <el-input
                    :model-value="currentUserInfo.phone || '未设置'"
                    disabled
                    placeholder="当前手机号"
                  />
                </el-form-item>

                <el-form-item label="新手机号" prop="new_phone">
                  <el-input
                    v-model="phoneForm.new_phone"
                    placeholder="请输入新手机号"
                    maxlength="11"
                  />
                </el-form-item>

                <el-form-item label="确认新手机号" prop="confirm_phone">
                  <el-input
                    v-model="phoneForm.confirm_phone"
                    placeholder="请再次输入新手机号"
                    maxlength="11"
                  />
                </el-form-item>

                <el-form-item>
                  <el-button
                    type="primary"
                    :loading="phoneLoading"
                    @click="changePhone"
                  >
                    修改手机号
                  </el-button>
                  <el-button @click="resetPhoneForm">
                    重置
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 其他设置 -->
        <el-tab-pane label="其他设置" name="other">
          <div class="other-settings">
            <el-alert
              title="更多设置功能开发中"
              type="info"
              :closable="false"
              show-icon
            />
            
            <div class="setting-item theme-setting">
              <h4>主题设置</h4>
              <p class="setting-description">选择您喜欢的主题风格</p>
              
              <!-- 简单的主题切换按钮 -->
              <div style="margin: 16px 0;">
                <el-button-group>
                  <el-button 
                    type="primary" 
                    :plain="currentThemeType !== 'default'"
                    @click="switchToTheme('default')"
                  >
                    默认主题
                  </el-button>
                  <el-button 
                    type="success" 
                    :plain="currentThemeType !== 'green'"
                    @click="switchToTheme('green')"
                  >
                    绿色主题
                  </el-button>
                  <el-button 
                    type="danger" 
                    :plain="currentThemeType !== 'pink'"
                    @click="switchToTheme('pink')"
                  >
                    粉色主题
                  </el-button>
                </el-button-group>
              </div>
              
              <p style="color: #666; font-size: 12px; margin-top: 12px;">当前主题：{{ 
                currentThemeType === 'green' ? '绿色主题' : 
                currentThemeType === 'pink' ? '粉色主题' : '默认主题' 
              }}</p>
            </div>
            
            <div class="setting-item">
              <h4>通知设置</h4>
              <p>消息通知设置功能即将上线</p>
            </div>
            
            <div class="setting-item">
              <h4>语言设置</h4>
              <p>多语言支持功能即将上线</p>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import {onMounted, onUnmounted, reactive, ref} from 'vue'
import type {FormInstance, FormRules} from 'element-plus'
import {ElMessage} from 'element-plus'
import {userApi} from '@/api/user'
import type {User} from '@/types/user'
// import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
// import { useThemeStore, type ThemeType } from '@/stores/theme'
// import { storeToRefs } from 'pinia'

const activeTab = ref('other')
const passwordFormRef = ref<FormInstance>()
const emailFormRef = ref<FormInstance>()
const phoneFormRef = ref<FormInstance>()
const passwordLoading = ref(false)
const emailLoading = ref(false)
const phoneLoading = ref(false)

// 简单的主题管理
const currentThemeType = ref<'default' | 'green' | 'pink'>('default')

// 主题颜色管理
const primaryColor = ref('#409eff')

// 更新主题颜色
const updateThemeColors = () => {
  const rootStyles = getComputedStyle(document.documentElement)
  const newPrimaryColor = rootStyles.getPropertyValue('--el-color-primary') || '#409eff'
  primaryColor.value = newPrimaryColor
  
  // 直接更新标签页下划线颜色
  setTimeout(() => {
    const activeBar = document.querySelector('.el-tabs__active-bar') as HTMLElement
    if (activeBar) {
      activeBar.style.backgroundColor = newPrimaryColor
    }
    
    const activeTab = document.querySelector('.el-tabs__item.is-active') as HTMLElement
    if (activeTab) {
      activeTab.style.color = newPrimaryColor
    }
  }, 50)
}

// 监听CSS变量变化
let observer: MutationObserver | null = null

// 初始化时读取本地存储的主题
const initTheme = () => {
  try {
    const savedTheme = localStorage.getItem('simple-theme') as 'default' | 'green' | 'pink' | null
    if (savedTheme && (savedTheme === 'default' || savedTheme === 'green' || savedTheme === 'pink')) {
      currentThemeType.value = savedTheme
      applyTheme(savedTheme)
      
      // 初始化标签页颜色
      const themeColors = {
        default: '#409eff',
        green: '#67c23a',
        pink: '#f56c6c'
      }
      
      setTimeout(() => {
        primaryColor.value = themeColors[savedTheme]
        updateThemeColors()
      }, 300)
    }
  } catch (error) {
    console.warn('读取主题设置失败:', error)
  }
}

const currentUserInfo = reactive<Partial<User>>({
  email: '',
  phone: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const emailForm = reactive({
  new_email: '',
  confirm_email: ''
})

const phoneForm = reactive({
  new_phone: '',
  confirm_phone: ''
})

// 自定义验证规则
const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateConfirmEmail = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入新邮箱'))
  } else if (value !== emailForm.new_email) {
    callback(new Error('两次输入的邮箱不一致'))
  } else {
    callback()
  }
}

const validateConfirmPhone = (_rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入新手机号'))
  } else if (value !== phoneForm.new_phone) {
    callback(new Error('两次输入的手机号不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const emailRules: FormRules = {
  new_email: [
    { required: true, message: '请输入新邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  confirm_email: [
    { required: true, validator: validateConfirmEmail, trigger: 'blur' }
  ]
}

const phoneRules: FormRules = {
  new_phone: [
    { required: true, message: '请输入新手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号格式', trigger: 'blur' }
  ],
  confirm_phone: [
    { required: true, validator: validateConfirmPhone, trigger: 'blur' }
  ]
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      passwordLoading.value = true
      try {
        await userApi.changePassword({
          old_password: passwordForm.old_password,
          new_password: passwordForm.new_password
        })
        
        ElMessage.success('密码修改成功')
        resetPasswordForm()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '密码修改失败')
      } finally {
        passwordLoading.value = false
      }
    }
  })
}

// 获取当前用户信息
const fetchCurrentUserInfo = async () => {
  try {
    const response = await userApi.getCurrentUserProfile()
    Object.assign(currentUserInfo, response.data)
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
}

// 修改邮箱
const changeEmail = async () => {
  if (!emailFormRef.value) return

  await emailFormRef.value.validate(async (valid) => {
    if (valid) {
      emailLoading.value = true
      try {
        await userApi.changeEmail({
          new_email: emailForm.new_email
        })

        ElMessage.success('邮箱修改成功')
        currentUserInfo.email = emailForm.new_email
        resetEmailForm()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '邮箱修改失败')
      } finally {
        emailLoading.value = false
      }
    }
  })
}

// 修改手机号
const changePhone = async () => {
  if (!phoneFormRef.value) return

  await phoneFormRef.value.validate(async (valid) => {
    if (valid) {
      phoneLoading.value = true
      try {
        await userApi.changePhone({
          new_phone: phoneForm.new_phone
        })

        ElMessage.success('手机号修改成功')
        currentUserInfo.phone = phoneForm.new_phone
        resetPhoneForm()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.message || '手机号修改失败')
      } finally {
        phoneLoading.value = false
      }
    }
  })
}

// 重置密码表单
const resetPasswordForm = () => {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordFormRef.value?.clearValidate()
}

// 重置邮箱表单
const resetEmailForm = () => {
  emailForm.new_email = ''
  emailForm.confirm_email = ''
  emailFormRef.value?.clearValidate()
}

// 重置手机号表单
const resetPhoneForm = () => {
  phoneForm.new_phone = ''
  phoneForm.confirm_phone = ''
  phoneFormRef.value?.clearValidate()
}

// 简单的主题应用方法
const applyTheme = (theme: 'default' | 'green' | 'pink') => {
  const root = document.documentElement
  
  if (theme === 'green') {
    // 绿色主题的CSS变量
    root.style.setProperty('--el-color-primary', '#67c23a')
    root.style.setProperty('--el-color-primary-light-3', '#95d475')
    root.style.setProperty('--el-color-primary-light-5', '#b3e19d')
    root.style.setProperty('--el-color-primary-light-7', '#d1edc4')
    root.style.setProperty('--el-color-primary-light-8', '#e1f3d8')
    root.style.setProperty('--el-color-primary-light-9', '#f0f9eb')
    root.style.setProperty('--el-color-primary-dark-2', '#529b2e')
    
    // 自定义侧边栏主题变量
    root.style.setProperty('--sidebar-bg-color', '#2d5016')
    root.style.setProperty('--sidebar-logo-bg-color', '#1f3a0f')
    root.style.setProperty('--sidebar-active-color', '#67c23a')
    root.style.setProperty('--sidebar-logo-icon-color', '#67c23a')
  } else if (theme === 'pink') {
    // 粉色主题的CSS变量
    root.style.setProperty('--el-color-primary', '#f56c6c')
    root.style.setProperty('--el-color-primary-light-3', '#fbc4c4')
    root.style.setProperty('--el-color-primary-light-5', '#fdd8d8')
    root.style.setProperty('--el-color-primary-light-7', '#feebeb')
    root.style.setProperty('--el-color-primary-light-8', '#fef0f0')
    root.style.setProperty('--el-color-primary-light-9', '#fef5f5')
    root.style.setProperty('--el-color-primary-dark-2', '#c45656')
    
    // 自定义侧边栏主题变量
    root.style.setProperty('--sidebar-bg-color', '#5c2d2d')
    root.style.setProperty('--sidebar-logo-bg-color', '#4a1f1f')
    root.style.setProperty('--sidebar-active-color', '#f56c6c')
    root.style.setProperty('--sidebar-logo-icon-color', '#f56c6c')
  } else {
    // 默认主题的CSS变量
    root.style.setProperty('--el-color-primary', '#409eff')
    root.style.setProperty('--el-color-primary-light-3', '#79bbff')
    root.style.setProperty('--el-color-primary-light-5', '#a0cfff')
    root.style.setProperty('--el-color-primary-light-7', '#c6e2ff')
    root.style.setProperty('--el-color-primary-light-8', '#d9ecff')
    root.style.setProperty('--el-color-primary-light-9', '#ecf5ff')
    root.style.setProperty('--el-color-primary-dark-2', '#337ecc')
    
    // 默认侧边栏主题变量
    root.style.setProperty('--sidebar-bg-color', '#304156')
    root.style.setProperty('--sidebar-logo-bg-color', '#2b2f3a')
    root.style.setProperty('--sidebar-active-color', '#409eff')
    root.style.setProperty('--sidebar-logo-icon-color', '#409eff')
  }
}

// 主题切换方法
const switchToTheme = (theme: 'default' | 'green' | 'pink') => {
  currentThemeType.value = theme
  applyTheme(theme)
  
  // 立即获取新的主题颜色
  const themeColors = {
    default: '#409eff',
    green: '#67c23a',
    pink: '#f56c6c'
  }
  
  const newColor = themeColors[theme]
  
  // 更新primaryColor变量
  primaryColor.value = newColor
  
  // 为标签页容器添加主题类名
  setTimeout(() => {
    const tabsContainers = document.querySelectorAll('.el-tabs')
    tabsContainers.forEach(container => {
      // 移除之前的主题类
      container.classList.remove('theme-default', 'theme-green', 'theme-pink')
      // 添加新的主题类
      container.classList.add(`theme-${theme}`)
    })
    
    // 为设置页面容器添加主题类名，确保标题装饰线也能响应主题
    const settingsContainer = document.querySelector('.settings-container')
    if (settingsContainer) {
      settingsContainer.classList.remove('theme-default', 'theme-green', 'theme-pink')
      settingsContainer.classList.add(`theme-${theme}`)
    }
    
    // 直接更新所有标题装饰线的颜色
    const sectionTitles = document.querySelectorAll('.section-title')
    sectionTitles.forEach(title => {
      const element = title as HTMLElement
      element.style.setProperty('border-left-color', newColor, 'important')
    })
    
    console.log('主题切换完成:', theme, newColor)
  }, 50)
  
  // 保存到本地存储
  try {
    localStorage.setItem('simple-theme', theme)
  } catch (error) {
    console.warn('保存主题设置失败:', error)
  }
  
  const themeNames = {
    default: '默认主题',
    green: '绿色主题',
    pink: '粉色主题'
  }
  
  // 使用自定义样式的消息提示，让颜色与主题一致
  ElMessage({
    message: `已切换到${themeNames[theme]}`,
    type: 'success',
    duration: 3000,
    customClass: `theme-message-${theme}`,
    showClose: true
  })
}

// 页面加载时获取用户信息和初始化主题
onMounted(() => {
  fetchCurrentUserInfo()
  initTheme()
  updateThemeColors()
  
  // 创建 MutationObserver 来监听 style 属性的变化
  observer = new MutationObserver(() => {
    updateThemeColors()
  })
  
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['style']
  })
})

// 组件销毁时清理监听器
onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.settings-card {
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

.settings-tabs {
  margin-top: 20px;
}

/* 完全隐藏原有的下划线 */
.settings-tabs :deep(.el-tabs__active-bar) {
  display: none !important;
  visibility: hidden !important;
  opacity: 0 !important;
}

/* 标签页文字颜色 */
.settings-tabs :deep(.el-tabs__item.is-active) {
  color: var(--el-color-primary) !important;
  position: relative;
}

.settings-tabs :deep(.el-tabs__item:hover) {
  color: var(--el-color-primary) !important;
}

/* 使用伪元素创建自定义下划线 */
.settings-tabs :deep(.el-tabs__item.is-active::after) {
  content: '' !important;
  position: absolute !important;
  bottom: 0 !important;
  left: 0 !important;
  right: 0 !important;
  height: 3px !important;
  background-color: var(--el-color-primary) !important;
  border-radius: 3px 3px 0 0 !important;
  z-index: 10 !important;
}

/* 基于主题类名的强制样式 */
.theme-green :deep(.el-tabs__item.is-active::after) {
  background-color: #67c23a !important;
}

.theme-green :deep(.el-tabs__item.is-active) {
  color: #67c23a !important;
}

.theme-pink :deep(.el-tabs__item.is-active::after) {
  background-color: #f56c6c !important;
}

.theme-pink :deep(.el-tabs__item.is-active) {
  color: #f56c6c !important;
}

.theme-default :deep(.el-tabs__item.is-active::after) {
  background-color: #409eff !important;
}

.theme-default :deep(.el-tabs__item.is-active) {
  color: #409eff !important;
}

/* 确保标签页容器有相对定位 */
.settings-tabs :deep(.el-tabs__nav) {
  position: relative !important;
}

.settings-tabs :deep(.el-tabs__item) {
  position: relative !important;
}

.settings-form {
  max-width: 500px;
  margin-top: 20px;
}

.other-settings {
  padding: 20px 0;
}

.setting-item {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fafafa;
}

.theme-setting {
  background-color: #fff;
  border: 1px solid #e4e7ed;
}

.setting-item h4 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 16px;
}

.setting-item p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.setting-description {
  margin-bottom: 16px !important;
}

/* 个人信息设置样式 */
.profile-settings {
  padding: 20px 0;
}

.setting-section {
  margin-bottom: 40px;
}

.section-title {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
  border-left: 4px solid var(--el-color-primary);
  padding-left: 12px;
  transition: border-color 0.3s ease;
}

/* 基于主题类名强制覆盖标题装饰线颜色 */
.theme-green .section-title {
  border-left-color: #67c23a !important;
}

.theme-pink .section-title {
  border-left-color: #f56c6c !important;
}

.theme-default .section-title {
  border-left-color: #409eff !important;
}

.settings-form {
  max-width: 500px;
  margin-top: 20px;
}

/* 分隔线样式 */
.el-divider {
  margin: 40px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-form {
    max-width: 100%;
  }

  .section-title {
    font-size: 16px;
  }

  .setting-section {
    margin-bottom: 30px;
  }
}

/* 主题相关的消息提示样式 */
:global(.theme-message-default) {
  background-color: #ecf5ff !important;
  border-color: #409eff !important;
  color: #409eff !important;
}

:global(.theme-message-default .el-message__icon) {
  color: #409eff !important;
}

:global(.theme-message-default .el-message__content) {
  color: #409eff !important;
}

:global(.theme-message-green) {
  background-color: #f0f9eb !important;
  border-color: #67c23a !important;
  color: #67c23a !important;
}

:global(.theme-message-green .el-message__icon) {
  color: #67c23a !important;
}

:global(.theme-message-green .el-message__content) {
  color: #67c23a !important;
}

:global(.theme-message-pink) {
  background-color: #fdf2f2 !important;
  border-color: #f56c6c !important;
  color: #f56c6c !important;
}

:global(.theme-message-pink .el-message__icon) {
  color: #f56c6c !important;
}

:global(.theme-message-pink .el-message__content) {
  color: #f56c6c !important;
}
</style>
