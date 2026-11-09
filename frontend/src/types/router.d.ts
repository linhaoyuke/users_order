import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    icon?: string
    requiresAuth?: boolean
    permission?: string
    permissions?: string[]
    roles?: string[]
    hidden?: boolean
  }
}

