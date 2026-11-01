-- =====================================================================
--  PostgreSQL 性能优化索引脚本
--  说明:
--  1. 此脚本专为 PostgreSQL 数据库设计。
--  2. 使用 'IF NOT EXISTS' 防止因索引已存在而导致的错误。
--  3. 建议在数据库负载较低的时段执行。
-- =====================================================================


-- =====================================================================
--  一、高优先级索引 (对核心功能有巨大影响)
-- =====================================================================

-- 1. `orders` 表的外键 `user_id`
--    用途: 极大地加速普通用户查询自身订单列表的操作。
--    对应代码: `order_api.py` -> `get_orders()`
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON public.orders (user_id);


-- 2. 【强烈推荐】`orders` 表的复合索引 `(user_id, created_at DESC)`
--    用途: 完美优化“查询某个用户最近的订单”这一最常见场景。
--         数据库可以利用此索引同时完成用户筛选和时间排序，效率极高。
CREATE INDEX IF NOT EXISTS idx_orders_user_created_at ON public.orders (user_id, created_at DESC);


-- 3. `users` 表的 `username` 和 `email`
--    注意: PostgreSQL 会为 UNIQUE 约束自动创建唯一索引。
--         以下命令主要用于确保索引存在，或在没有 UNIQUE 约束时手动创建。
--    用途: 加速注册和修改用户信息时检查用户名和邮箱是否已存在。
--    对应代码: `user_api.py` -> `create_user()`, `update_user()`
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON public.users (username);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON public.users (email);


-- =====================================================================
--  二、中优先级索引 (主要优化后台管理的筛选和排序功能)
-- =====================================================================

-- 1. `orders` 表的 `status` 字段
--    用途: 加速管理员按订单状态筛选订单。
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders (status);


-- 2. `orders` 表的 `payment_status` 字段
--    用途: 加速管理员按支付状态筛选订单。
CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON public.orders (payment_status);


-- 3. `orders` 表的 `created_at` 字段
--    用途: 加速按创建时间进行范围查找和排序。
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders (created_at);


-- 4. `orders` 表的复合索引 `(status, payment_status)`
--    用途: 优化管理员同时按“订单状态”和“支付状态”进行组合筛选的场景。
CREATE INDEX IF NOT EXISTS idx_orders_status_payment ON public.orders (status, payment_status);

--在 order_items 表中，order_id 和 product_id 是外键。PostgreSQL
--不会自动为外键创建索引。当查询一个订单及其所有项目时（一个非常常见的操作），需要在 order_items 上通过
--order_id 进行连接（JOIN），没有索引会导致全表扫描，性能会随着订单量的增长急剧下降。
--建议: 为 order_items.order_id 和 order_items.product_id 添加索引。
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON public.order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON public.order_items (product_id);

-- =====================================================================
--  脚本结束
-- =====================================================================
