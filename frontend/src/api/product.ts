import request from '@/utils/request'
import type {Product} from '@/types/product'
import type {PaginatedResponse} from '@/types/api'

// 定义创建和更新商品时用的表单类型
export interface ProductForm {
  name: string
  description?: string
  price: number
  stock: number
}

export interface GetProductsParams {
  name?: string
  page?: number
  per_page?: number
}

export const productApi = {
  // 获取商品列表 (可带参数)
  getProducts: (params?: GetProductsParams) => {
    return request.get<PaginatedResponse<Product>>('/products/', { params })
  },

  // 获取单个商品详情
  getProduct: (id: string) => {
    return request.get<Product>(`/products/${id}`)
  },

  // 创建新商品
  createProduct: (data: ProductForm) => {
    return request.post<Product>('/products/', data)
  },

  // 更新商品信息
  updateProduct: (id: string, data: Partial<ProductForm>) => {
    return request.put<Product>(`/products/${id}`, data)
  },

  // 删除商品
  deleteProduct: (id: string) => {
    return request.delete(`/products/${id}`)
  }
}
