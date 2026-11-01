import request from '@/utils/request'

export interface DashboardStats {
  user_stats: {
    total_users: number
    active_users: number
  }
  order_stats: {
    total_orders: number
    pending_orders: number
    completed_orders: number
    total_amount: number
  }
  role_stats: {
    total_roles: number
    active_roles: number
  }
  permission_stats: {
    total_permissions: number
    active_permissions: number
  }
  product_stats: {
    total_products: number
    in_stock_products: number
  }
}

export const statsApi = {
  // 获取仪表盘统计数据
  getDashboardStats: () => {
    return request.get<DashboardStats>('/stats/dashboard')
  }
}
