export interface LoginForm {
  username: string
  password: string
  captcha: string
  captcha_token: string
}

export interface Permission {
  id: number
  name: string
  code: string
  description?: string
  resource: string
  action: string
}

export interface Role {
  id: number
  name: string
  code: string
  description?: string
  permissions?: Permission[]
}

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  phone?: string
  is_active: boolean
  created_at: string
  updated_at: string
  roles: Role[]
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  user: User
}

export interface JwtPayload {
  exp: number
  iat: number
  jti: string
  sub: string
  type: string
  id: number
  username: string
  email: string
  full_name: string | null
  is_active: boolean
  roles: { id: number; name: string; code: string }[]
  permissions: string[]
}
