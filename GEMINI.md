# GEMINI.md

## 项目概述

这是一个全栈 Web 应用程序，前端使用 Vue.js，后端使用 Python Flask。该应用程序似乎是一个用户和订单管理系统。

**前端:**

*   **框架:** Vue.js 3
*   **构建工具:** Vite
*   **语言:** TypeScript
*   **UI 库:** Element Plus
*   **状态管理:** Pinia
*   **HTTP 客户端:** Axios

**后端:**

*   **框架:** Flask
*   **包管理器:** uv
*   **数据库:** PostgreSQL (从 `psycopg2-binary` 推断)
*   **认证:** JWT

## 构建和运行

**前端:**

1.  **安装依赖:**
    ```bash
    cd frontend
    npm install
    ```
2.  **运行开发服务器:**
    ```bash
    npm run dev
    ```
3.  **构建生产版本:**
    ```bash
    npm run build
    ```

**后端:**

1.  **安装依赖:**
    ```bash
    cd backend
    uv sync
    ```
2.  **运行开发服务器:**
    ```bash
    flask run
    ```
3.  **在生产环境中运行 (使用 Waitress):**
    ```bash
    waitress-serve --host 0.0.0.0 --port 5000 app:app
    ```

## 开发约定

*   后端使用 `uv` 进行包管理，所有依赖项都在 `pyproject.toml` 中列出。
*   前端使用 `npm` 进行包管理。
*   后端遵循标准的 Flask 应用程序结构，为不同的 API 端点使用蓝图。
*   前端具有组织良好的结构，对组件、视图、存储和 API 有明确的关注点分离。
*   API 请求集中在 `frontend/src/utils/request.ts` 文件中。
