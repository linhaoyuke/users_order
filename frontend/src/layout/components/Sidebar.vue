<template>
  <div class="sidebar-container">
    <!-- Logo区域 -->
    <div class="logo-container">
      <el-icon class="logo-icon" v-if="!collapse"><Setting /></el-icon>
      <el-icon class="logo-icon-collapsed" v-else><Setting /></el-icon>
      <span class="title" v-if="!collapse">管理系统</span>
    </div>
    
    <!-- 动态菜单 -->
    <el-menu
      :default-active="activeMenu"
      :collapse="collapse"
      :unique-opened="true"
      :background-color="sidebarBgColor"
      text-color="#bfcbd9"
      :active-text-color="sidebarActiveColor"
      router
    >
      <template v-for="route in menuRoutes" :key="route.path">
        <!-- 只渲染有子菜单的项 -->
        <el-sub-menu v-if="route.children && route.children.length > 0" :index="route.path">
          <template #title>
            <el-icon v-if="route.meta?.icon"><component :is="route.meta.icon" /></el-icon>
            <span>{{ route.meta?.title }}</span>
          </template>
          <el-menu-item 
            v-for="child in route.children" 
            :key="child.path" 
            :index="child.path"
          >
            <el-icon v-if="child.meta?.icon"><component :is="child.meta.icon" /></el-icon>
            <template #title>{{ child.meta?.title }}</template>
          </el-menu-item>
        </el-sub-menu>
        <!-- 渲染没有子菜单的项 -->
        <el-menu-item v-else :index="route.path">
          <el-icon v-if="route.meta?.icon"><component :is="route.meta.icon" /></el-icon>
          <template #title>{{ route.meta?.title }}</template>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import {Setting} from '@element-plus/icons-vue'

defineProps<{ collapse: boolean }>()

const router = useRouter()
const currentRoute = useRoute()
const authStore = useAuthStore()

// 获取当前激活的菜单路径
const activeMenu = computed(() => currentRoute.path)

// 使用 ref 来存储CSS变量值，使其响应式
const sidebarBgColor = ref('#304156')
const sidebarActiveColor = ref('#409eff')

// 更新CSS变量值的方法
const updateThemeColors = () => {
  const rootStyles = getComputedStyle(document.documentElement)
  sidebarBgColor.value = rootStyles.getPropertyValue('--sidebar-bg-color') || '#304156'
  sidebarActiveColor.value = rootStyles.getPropertyValue('--sidebar-active-color') || '#409eff'
}

// 监听CSS变量变化
let observer: MutationObserver | null = null

onMounted(() => {
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

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})

// 从路由配置中过滤出需要在菜单中显示的路由
const menuRoutes = computed(() => {
  const allRoutes = router.options.routes
  const layoutRoute = allRoutes.find(r => r.name === 'Layout')
  
  if (!layoutRoute || !layoutRoute.children) {
    return []
  }

  // 过滤子路由
  return layoutRoute.children.filter(child => {
    // 如果路由被标记为隐藏，则不显示
    if (child.meta?.hidden) {
      return false
    }
    // 如果路由需要权限，则检查用户是否拥有该权限
    if (child.meta?.permission) {
      return authStore.hasPermission(child.meta.permission as string)
    }
    // 如果没有指定权限，则默认显示
    return true
  })
})
</script>

<style scoped>
.sidebar-container {
  height: 100%;
}
.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--sidebar-logo-bg-color, #2b2f3a);
  border-bottom: 1px solid #464c5b;
}
.logo-icon {
  font-size: 32px;
  color: var(--sidebar-logo-icon-color, #409eff);
  margin-right: 8px;
}
.logo-icon-collapsed {
  font-size: 24px;
  color: var(--sidebar-logo-icon-color, #409eff);
}
.title {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}
.el-menu {
  border-right: none;
  height: calc(100vh - 60px);
}
.el-menu:not(.el-menu--collapse) {
  width: 200px;
}
</style>

