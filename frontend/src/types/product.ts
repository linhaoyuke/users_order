// src/types/product.ts

export interface Product {
  id: string
  name: string
  description: string | null
  price: number | string // 后端可能是 Numeric，前端接收时可能是字符串
  stock: number
  initial_stock: number
  created_at: string
  updated_at: string
}
