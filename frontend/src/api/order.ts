import request from '@/utils/request'
import type {CreateOrderForm, Order, UpdateOrderForm} from '@/types/order'

export interface OrderListResponse {
  items: Order[]
  total: number
  page: number
  per_page: number
  pages: number
}

export const orderApi = {
  // 获取订单列表
  getOrders: (params?: any) => {
    return request.get<OrderListResponse>('/orders/', { params })
  },

  // 获取订单详情
  getOrder: (id: string) => {
    return request.get<Order>(`/orders/${id}`)
  },

  // 创建订单
  createOrder: (data: CreateOrderForm) => {
    return request.post<Order>('/orders/', data)
  },

  // 更新订单
  updateOrder: (id: string, data: UpdateOrderForm) => {
    return request.put<Order>(`/orders/${id}`, data)
  },

  // 删除订单
  deleteOrder: (id: string) => {
    return request.delete(`/orders/${id}`)
  }
}
