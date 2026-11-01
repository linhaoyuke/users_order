import type { Product } from './product'

export interface OrderItem {
  id: string
  order_id: string
  product_id: string
  quantity: number
  unit_price: number // 下单时的价格快照
  subtotal: number
  product: Product // 嵌套的商品详情
}

export interface Order {
  id: string
  user_id: number
  user_username?: string
  user_full_name?: string
  order_number: string
  total_amount: number
  status: string
  payment_status: string
  shipping_address?: string
  created_at: string
  updated_at: string
  items: OrderItem[]
}

// 创建订单时，前端需要提交的数据结构
export interface CreateOrderForm {
  user_id: number | null
  shipping_address?: string
  items: {
    product_id: string
    quantity: number
  }[]
}

export interface UpdateOrderForm {
  status?: string
  payment_status?: string
  shipping_address?: string
  items?: {
    product_id: string
    quantity: number
  }[]
}

export const ORDER_STATUS = {
  PENDING_PAYMENT: 'pending_payment',
  PAID: 'paid',
  SHIPPED: 'shipped',
  DELIVERED: 'delivered',
  CANCELLED: 'cancelled'
} as const

export const PAYMENT_STATUS = {
  UNPAID: 'unpaid',
  PAID: 'paid',
  REFUNDED: 'refunded'
} as const

export const ORDER_STATUS_LABELS = {
  [ORDER_STATUS.PENDING_PAYMENT]: '待付款',
  [ORDER_STATUS.PAID]: '已付款',
  [ORDER_STATUS.SHIPPED]: '已发货',
  [ORDER_STATUS.DELIVERED]: '已送达',
  [ORDER_STATUS.CANCELLED]: '已取消'
}

export const PAYMENT_STATUS_LABELS = {
  [PAYMENT_STATUS.UNPAID]: '未付款',
  [PAYMENT_STATUS.PAID]: '已付款',
  [PAYMENT_STATUS.REFUNDED]: '已退款'
}
