# QWEN.md

## 项目概述

这是一个全栈 Web 应用程序，前端使用 Vue.js (Vite)，后端使用 Python Flask。该应用程序是一个用户和订单管理系统，同时也包含商品管理功能。

*   **前端:**
    *   **框架:** Vue.js 3 (Composition API)
    *   **构建工具:** Vite
    *   **语言:** TypeScript
    *   **UI 库:** Element Plus
    *   **状态管理:** Pinia
    *   **HTTP 客户端:** Axios
    *   **路由:** Vue Router
*   **后端:**
    *   **框架:** Flask
    *   **包管理器:** uv (通过 `pyproject.toml` 管理依赖)
    *   **数据库:** PostgreSQL
    *   **认证:** JWT (使用 `flask-jwt-extended`)
    *   **缓存/Session:** Redis (使用 `flask-caching` 和 `flask-session`)
    *   **ORM:** SQLAlchemy
*   **数据库:** PostgreSQL 脚本 (`init_db.sql`) 用于初始化表结构、初始数据和触发器。

## 构建和运行

### 前端 (frontend)

1.  **安装依赖:**
    ```bash
    cd frontend
    npm install
    ```
2.  **运行开发服务器:**
    ```bash
    npm run dev
    ```
    *   开发服务器默认运行在 `http://localhost:3000`。
    *   Vite 配置了代理，将 `/api` 请求转发到后端 `http://localhost:5000`。
3.  **构建生产版本:**
    ```bash
    npm run build
    ```
4.  **类型检查:**
    ```bash
    npm run type-check
    ```

### 后端 (backend)

1.  **安装依赖:**
    ```bash
    cd backend
    # 确保你使用的是 Python 3.12 或更高版本
    # 使用 uv 安装依赖
    uv sync
    ```
2.  **环境变量:**
    *   后端配置通过 `backend/.env` 文件加载 (由 `backend/config.py` 处理)。需要配置 `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL` 和 `CACHE_REDIS_URL`。
3.  **运行开发服务器:**
    ```bash
    # 在 backend 目录下
    flask run
    ```
    *   开发服务器默认运行在 `http://localhost:5000`。
    *   `backend/.flaskenv` 设置了 `FLASK_ENV=development`，但代码中强制在生产模式下运行。
4.  **在生产环境中运行 (使用 Waitress):**
    ```bash
    # 在 backend 目录下
    waitress-serve --host 0.0.0.0 --port 5000 app:app
    ```

### 数据库初始化

*   使用 `init_db.sql` 脚本在 PostgreSQL 数据库中创建表、触发器和填充初始数据。
    ```sql
    -- 在 PostgreSQL 命令行或工具中执行
    \i path/to/init_db.sql
    ```

## 开发约定

*   **后端依赖管理:** 使用 `uv` 和 `pyproject.toml` 进行包管理。
*   **前端依赖管理:** 使用 `npm` 和 `package.json` 进行包管理。
*   **后端架构:**
    *   遵循标准的 Flask 应用程序结构。
    *   使用工厂模式创建应用 (`app.py`)。
    *   使用蓝图 (`api/api.py`) 组织 API 端点。
    *   使用 `config.py` 管理配置。
    *   使用 `extensions.py` 初始化 Flask 扩展 (db, jwt, cache, session)。
    *   使用 `models/` 目录存放 SQLAlchemy 数据模型。
    *   使用 `utils/` 目录存放工具函数 (如 JWT 处理)。
*   **前端架构:**
    *   具有组织良好的结构，对组件 (`components/`)、视图/页面 (`views/`)、存储 (`stores/`)、API 请求 (`utils/request.ts`) 和路由 (`router/`) 有明确的关注点分离。
    *   使用 Pinia 进行状态管理。
    *   使用 TypeScript 和 Composition API。
    *   使用 `@` 作为 `src/` 目录的别名。
*   **认证:** 前后端通过 JWT 进行用户认证。
*   **API:** 前端通过 `frontend/src/utils/request.ts` 中的 Axios 实例与后端 `/api` 端点通信。
