import type { Role } from './auth'

export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  phone?: string
  is_active: boolean
  created_at: string
  updated_at: string
  roles: Role[]
}

export interface CreateUserForm {
  username: string
  password: string
  email: string
  full_name?: string
  phone?: string
  is_active?: boolean
  role_ids?: number[]
}

export interface UpdateUserForm {
  username?: string
  email?: string
  full_name?: string
  phone?: string
  is_active?: boolean
  role_ids?: number[]
}
