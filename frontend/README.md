# 后台管理系统前端

基于 Vue3 + Vite + TypeScript + Element Plus 构建的现代化后台管理系统前端。

## 功能特性

- 🚀 **现代化技术栈**: Vue3 + Vite + TypeScript + Element Plus
- 🔐 **完整的认证系统**: JWT token 管理、路由守卫、权限控制
- 👥 **用户管理**: 用户增删改查、角色分配、状态管理
- 🛡️ **权限管理**: 角色管理、权限管理、角色权限分配
- 📦 **订单管理**: 订单列表、订单详情、状态管理、订单项管理
- 📱 **响应式设计**: 支持桌面端和移动端
- 🎨 **美观的UI**: 基于 Element Plus 的现代化界面设计

## 技术栈

- **框架**: Vue 3.4+
- **构建工具**: Vite 5.0+
- **语言**: TypeScript 5.3+
- **UI库**: Element Plus 2.4+
- **状态管理**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP客户端**: Axios 1.6+
- **日期处理**: Day.js 1.11+

## 项目结构

```
src/
├── api/                 # API接口定义
│   ├── auth.ts         # 认证相关接口
│   ├── user.ts         # 用户管理接口
│   ├── role.ts         # 角色管理接口
│   ├── permission.ts   # 权限管理接口
│   └── order.ts        # 订单管理接口
├── components/         # 通用组件
│   └── TablePage.vue   # 表格页面组件
├── layout/             # 布局组件
│   ├── index.vue       # 主布局
│   └── components/     # 布局子组件
├── router/             # 路由配置
│   └── index.ts        # 路由定义
├── stores/             # 状态管理
│   └── auth.ts         # 认证状态
├── styles/             # 样式文件
│   └── index.css       # 全局样式
├── types/              # TypeScript类型定义
│   ├── auth.ts         # 认证相关类型
│   ├── user.ts         # 用户相关类型
│   └── order.ts        # 订单相关类型
├── utils/              # 工具函数
│   ├── request.ts      # HTTP请求封装
│   └── date.ts         # 日期处理工具
├── views/              # 页面组件
│   ├── auth/           # 认证页面
│   ├── dashboard/      # 仪表盘
│   ├── users/          # 用户管理
│   ├── roles/          # 角色管理
│   ├── permissions/    # 权限管理
│   ├── orders/         # 订单管理
│   └── error/          # 错误页面
├── App.vue             # 根组件
└── main.ts             # 应用入口
```

## 快速开始

### 环境要求

- Node.js 18+ 
- npm 9+ 或 yarn 1.22+ 或 pnpm 8+

### 安装依赖

```bash
# 使用 npm
npm install

# 使用 yarn
yarn install

# 使用 pnpm
pnpm install
```

### 启动开发服务器

```bash
# 使用 npm
npm run dev

# 使用 yarn
yarn dev

# 使用 pnpm
pnpm dev
```

访问 http://localhost:3000 查看应用。

### 构建生产版本

```bash
# 使用 npm
npm run build

# 使用 yarn
yarn build

# 使用 pnpm
pnpm build
```

### 预览生产版本

```bash
# 使用 npm
npm run preview

# 使用 yarn
yarn preview

# 使用 pnpm
pnpm preview
```

## 后端API配置

确保后端服务运行在 `http://localhost:5000`，或者修改 `.env.development` 文件中的 `VITE_API_BASE_URL` 配置。

### 后端API端点

- **认证**: `/api/auth/login`, `/api/auth/logout`, `/api/auth/refresh`
- **用户管理**: `/api/users/`
- **角色管理**: `/api/roles/`
- **权限管理**: `/api/permissions/`
- **订单管理**: `/api/orders/`

## 默认账号

- **管理员账号**: admin / admin123
- **普通用户**: 根据后端初始化数据

## 开发指南

### 添加新页面

1. 在 `src/views/` 下创建页面组件
2. 在 `src/router/index.ts` 中添加路由配置
3. 在侧边栏菜单中添加导航项（如需要）

### 添加新API

1. 在 `src/types/` 下定义相关类型
2. 在 `src/api/` 下创建API接口函数
3. 在页面组件中调用API

### 权限控制

使用 `useAuthStore` 中的 `hasPermission` 和 `hasRole` 方法进行权限判断：

```typescript
const authStore = useAuthStore()

// 检查权限
if (authStore.hasPermission('user:create')) {
  // 有创建用户权限
}

// 检查角色
if (authStore.hasRole('admin')) {
  // 是管理员
}
```

## 部署

### 使用 Nginx

1. 构建项目: `npm run build`
2. 将 `dist` 目录内容部署到 Nginx 静态文件目录
3. 配置 Nginx 反向代理到后端API

示例 Nginx 配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 许可证

MIT License
