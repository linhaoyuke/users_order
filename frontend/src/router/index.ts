import type {RouteRecordRaw} from 'vue-router'
import {createRouter, createWebHistory} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import {ElMessage} from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: { title: '403 - 无权访问', requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'Dashboard' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/index.vue'),
        meta: { title: '用户管理', icon: 'User', permission: 'view_user' }
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/roles/index.vue'),
        meta: { title: '角色管理', icon: 'UserFilled', permission: 'manage_role' }
      },
      {
        path: 'permissions',
        name: 'Permissions',
        component: () => import('@/views/permissions/index.vue'),
        meta: { title: '权限管理', icon: 'Lock', permission: 'manage_role' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/orders/index.vue'),
        meta: { title: '订单管理', icon: 'ShoppingCart', permission: 'view_order' }
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/products/index.vue'),
        meta: { title: '商品管理', icon: 'Goods', permission: 'view_product' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/index.vue'),
        meta: { title: '个人信息', icon: 'User', hidden: true }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '系统设置', icon: 'Setting', hidden: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404 - 页面未找到', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：登录状态认证与细粒度权限拦截（防止直接修改 URL 发生越权访问）
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const hasToken = !!authStore.token

  // 1. 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 管理系统`
  }

  // 2. 检查路由层级是否需要登录认证
  const requiresAuth = to.matched.some(record => record.meta?.requiresAuth)

  if (requiresAuth && !hasToken) {
    ElMessage.warning('请先登录系统')
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 3. 已登录状态下访问登录页，自动重定向至首页
  if (to.name === 'Login' && hasToken) {
    next({ path: '/' })
    return
  }

  // 4. 细粒度权限检查（针对需要认证的路由记录）
  if (hasToken) {
    for (const record of to.matched) {
      // 检查单一权限编码
      if (record.meta?.permission) {
        if (!authStore.hasPermission(record.meta.permission)) {
          ElMessage.warning('您暂无权限访问该页面')
          next({ name: 'Forbidden', query: { from: to.fullPath } })
          return
        }
      }

      // 检查多权限编码（具备其一即可访问）
      if (record.meta?.permissions && Array.isArray(record.meta.permissions)) {
        if (!authStore.hasAnyPermission(record.meta.permissions)) {
          ElMessage.warning('您暂无权限访问该页面')
          next({ name: 'Forbidden', query: { from: to.fullPath } })
          return
        }
      }

      // 检查特定角色要求
      if (record.meta?.roles && Array.isArray(record.meta.roles)) {
        const hasRequiredRole = record.meta.roles.some(roleCode => authStore.hasRole(roleCode))
        if (!hasRequiredRole) {
          ElMessage.warning('您所属角色暂无权限访问该页面')
          next({ name: 'Forbidden', query: { from: to.fullPath } })
          return
        }
      }
    }
  }

  // 5. 权限验证通过，允许跳转
  next()
})

export default router
