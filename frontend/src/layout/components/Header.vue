<template>
  <div class="header-container">
    <div class="header-left">
      <!-- 折叠按钮 -->
      <el-button
        type="text"
        size="large"
        @click="$emit('toggle-sidebar')"
        class="collapse-btn"
        :style="{ color: primaryColor }"
      >
        <el-icon>
          <Expand v-if="collapse" />
          <Fold v-else />
        </el-icon>
      </el-button>
      
      <!-- 面包屑 -->
      <el-breadcrumb separator="/" :style="{ color: primaryColor }">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="currentRoute.meta?.title">
          {{ currentRoute.meta.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    
    <div class="header-right">
      <!-- 用户信息 -->
      <el-dropdown @command="handleCommand">
        <span class="user-info">
          <el-avatar :size="32" :src="userAvatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <span class="username" :style="{ color: primaryColor }">{{ authStore.user?.full_name || authStore.user?.username }}</span>
          <el-icon class="arrow-down"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">
              <el-icon><User /></el-icon>
              个人信息
            </el-dropdown-item>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>
              设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>
              退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {ElMessageBox} from 'element-plus'
import {useAuthStore} from '@/stores/auth'

interface Props {
  collapse: boolean
}

defineProps<Props>()
defineEmits<{
  'toggle-sidebar': []
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentRoute = computed(() => route)
const userAvatar = computed(() => '')

// 主题颜色管理
const primaryColor = ref('#606266')

// 更新主题颜色
const updateThemeColors = () => {
  const rootStyles = getComputedStyle(document.documentElement)
  primaryColor.value = rootStyles.getPropertyValue('--el-color-primary') || '#409eff'
}

// 监听CSS变量变化
let observer: MutationObserver | null = null

onMounted(() => {
  updateThemeColors()
  
  observer = new MutationObserver(() => {
    updateThemeColors()
  })
  
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['style']
  })
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

const handleCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人信息页面
      router.push('/profile')
      break
    case 'settings':
      // 跳转到设置页面
      router.push('/settings')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        await authStore.logout()
        router.push('/login')
      } catch (error) {
        // 用户取消
      }
      break
  }
}
</script>

<style scoped>
.header-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  margin-right: 20px;
  /* color: #606266; 移除固定颜色，使用动态设置 */
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  margin: 0 8px;
  /* color: #606266; 移除固定颜色，使用动态设置 */
  font-size: 14px;
  font-weight: 500;
}

.arrow-down {
  color: #c0c4cc;
  font-size: 12px;
}
</style>
