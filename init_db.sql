-- =====================================================================
--  PostgreSQL 数据库初始化脚本
--  功能:
--  1. 创建所有应用所需的表 (permissions, roles, users, products, orders, etc.)。
--  2. 创建一个触发器以自动更新 'updated_at' 时间戳。
--  3. 插入初始数据：权限、角色、商品。
--  4. 创建一个默认的 admin 用户，并赋予其所有权限。
-- =====================================================================


-- =====================================================================
--  一、辅助函数与触发器 (用于自动更新 updated_at)
-- =====================================================================
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';


-- =====================================================================
--  二、表结构创建
-- =====================================================================

-- 权限表
CREATE TABLE IF NOT EXISTS public.permissions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(100),
    action VARCHAR(100)
);

-- 角色表
CREATE TABLE IF NOT EXISTS public.roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- 用户表
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- 为 users 表附加 updated_at 触发器
DROP TRIGGER IF EXISTS update_users_modtime ON public.users;
CREATE TRIGGER update_users_modtime BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

-- 商品表 (新增)
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    initial_stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- 为 products 表附加 updated_at 触发器
DROP TRIGGER IF EXISTS update_products_modtime ON public.products;
CREATE TRIGGER update_products_modtime BEFORE UPDATE ON public.products FOR EACH ROW EXECUTE PROCEDURE update_modified_column();


-- 订单表
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    order_number BIGINT UNIQUE NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending_payment',
    payment_status VARCHAR(50) DEFAULT 'unpaid',
    shipping_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- 为 orders 表附加 updated_at 触发器
DROP TRIGGER IF EXISTS update_orders_modtime ON public.orders;
CREATE TRIGGER update_orders_modtime BEFORE UPDATE ON public.orders FOR EACH ROW EXECUTE PROCEDURE update_modified_column();


-- 订单项表 (修改)
CREATE TABLE IF NOT EXISTS public.order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES public.orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE RESTRICT, -- 关键改动
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL, -- 下单时商品价格的快照
    subtotal NUMERIC(10, 2) NOT NULL
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS public.operation_logs (
    id BIGSERIAL PRIMARY KEY,
    operator_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    operator_username VARCHAR(50),
    operator_name VARCHAR(100),
    module VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    resource_name VARCHAR(200),
    description TEXT NOT NULL,
    old_values TEXT,
    new_values TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_method VARCHAR(10),
    request_url TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);


-- =====================================================================
--  三、多对多关联表
-- =====================================================================

-- 用户-角色 关联表
CREATE TABLE IF NOT EXISTS public.user_roles (
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- 角色-权限 关联表
CREATE TABLE IF NOT EXISTS public.role_permissions (
    role_id BIGINT NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
    permission_id BIGINT NOT NULL REFERENCES public.permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);


-- =====================================================================
--  四、初始数据填充
-- =====================================================================

-- 插入权限 (新增商品管理权限)
INSERT INTO public.permissions (name, code, description, resource, action) VALUES
('查看用户', 'view_user', '允许查看用户列表和详情', 'user', 'view'),
('管理用户', 'manage_user', '允许创建、编辑、删除用户', 'user', 'manage'),
('查看角色', 'view_role', '允许查看角色列表和详情', 'role', 'view'),
('管理角色', 'manage_role', '允许创建、编辑、删除角色和分配权限', 'role', 'manage'),
('查看订单', 'view_order', '允许查看订单列表和详情', 'order', 'view'),
('管理订单', 'manage_order', '允许创建、编辑、删除订单', 'order', 'manage'),
('查看商品', 'view_product', '允许查看商品列表', 'product', 'view'),
('管理商品', 'manage_product', '允许创建、编辑、删除商品', 'product', 'manage'),
('查看统计', 'view_stats', '允许查看仪表盘统计数据', 'stats', 'view')
ON CONFLICT (code) DO NOTHING;

-- 插入角色
INSERT INTO public.roles (name, code, description) VALUES
('管理员', 'admin', '拥有系统所有权限'),
('普通用户', 'user', '拥有基础查看权限')
ON CONFLICT (code) DO NOTHING;

-- 插入默认的 admin 用户
-- 密码是 'admin123' 的哈希值
-- 哈希值: scrypt:32768:8:1$WlAgs9OqQgyCWl6V$e7f07d453281435f9b915e2fe2a2ce44dcc26fe2e3c11493fae0009a846e12a3698b3ebc4d5d0bebadb1655b77f7584b43da353fdfb6fad642f1741e473b6885
INSERT INTO public.users (username, email, password, is_active, full_name) VALUES
('admin', 'admin@example.com', 'scrypt:32768:8:1$WlAgs9OqQgyCWl6V$e7f07d453281435f9b915e2fe2a2ce44dcc26fe2e3c11493fae0009a846e12a3698b3ebc4d5d0bebadb1655b77f7584b43da353fdfb6fad642f1741e473b6885', true, '系统管理员')
ON CONFLICT (username) DO NOTHING;

-- 插入示例商品 (新增)
INSERT INTO public.products (name, description, price, stock, initial_stock) VALUES
('高品质T恤', '100%纯棉，舒适透气', 99.00, 200, 200),
('经典牛仔裤', '修身剪裁，耐磨面料', 249.50, 150, 150),
('运动跑鞋', '轻便缓震，专业设计', 499.00, 80, 80),
('商务双肩包', '多功能分区，防水耐用', 320.00, 100, 100)
ON CONFLICT (name) DO NOTHING;


-- =====================================================================
--  五、数据关联
-- =====================================================================

-- 为 'admin' 角色分配所有权限
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT
    (SELECT id FROM public.roles WHERE code = 'admin'),
    p.id
FROM public.permissions p
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- 为 'user' 角色分配基础权限 (示例)
INSERT INTO public.role_permissions (role_id, permission_id)
SELECT
    (SELECT id FROM public.roles WHERE code = 'user'),
    p.id
FROM public.permissions p
WHERE p.code IN ('view_order', 'view_product')
ON CONFLICT (role_id, permission_id) DO NOTHING;


-- 为 'admin' 用户分配 '管理员' 角色
INSERT INTO public.user_roles (user_id, role_id)
SELECT
    (SELECT id FROM public.users WHERE username = 'admin'),
    (SELECT id FROM public.roles WHERE code = 'admin')
ON CONFLICT (user_id, role_id) DO NOTHING;


-- =====================================================================
--  六、额外数据填充 (由 Gemini 添加)
-- =====================================================================

-- 1. 额外权限
INSERT INTO public.permissions (name, code, description, resource, action) VALUES
('导出数据', 'export_data', '允许导出数据报表', 'system', 'export'),
('查看系统日志', 'view_logs', '允许查看系统操作日志', 'system', 'logs'),
('管理系统设置', 'manage_settings', '允许修改系统级别设置', 'system', 'settings'),
('发送通知', 'send_notifications', '允许向用户发送通知', 'notification', 'send'),
('审核内容', 'moderate_content', '允许审核用户提交的内容', 'content', 'moderate')
ON CONFLICT (code) DO NOTHING;

-- 2. 额外角色
INSERT INTO public.roles (name, code, description) VALUES
('财务经理', 'finance_manager', '负责处理财务和订单'),
('运营专员', 'operations_specialist', '负责商品和库存管理'),
('客服主管', 'customer_service_supervisor', '管理客服团队和处理用户问题'),
('数据分析师', 'data_analyst', '查看和分析系统数据'),
('内容审核员', 'content_moderator', '负责审核用户生成的内容'),
('市场推广', 'marketing_specialist', '负责市场活动和推广'),
('仓库管理员', 'warehouse_manager', '管理实体库存'),
('采购经理', 'procurement_manager', '负责采购商品'),
('技术支持', 'tech_support', '提供技术支持'),
('实习生', 'intern', '有限的访问权限')
ON CONFLICT (code) DO NOTHING;

-- 3. 额外商品
INSERT INTO public.products (name, description, price, stock, initial_stock) VALUES
('无线蓝牙耳机', '降噪功能，超长待机', 599.00, 120, 120),
('机械键盘', '青轴，RGB背光', 450.00, 70, 70),
('高清网络摄像头', '1080P，带麦克风', 199.00, 90, 90),
('人体工学椅', '保护脊椎，舒适办公', 1299.00, 50, 50),
('智能手表', '心率监测，运动记录', 899.00, 110, 110),
('便携式咖啡机', '随时随地享受咖啡', 299.00, 60, 60),
('电动牙刷', '声波震动，多种模式', 189.00, 150, 150),
('桌面加湿器', '静音运行，缓解干燥', 99.00, 200, 200),
('多口USB充电器', '快速充电，智能分流', 129.00, 180, 180),
('笔记本电脑支架', '铝合金材质，可调节', 159.00, 130, 130)
ON CONFLICT (name) DO NOTHING;

-- 4. 额外用户
-- 密码均为 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b'
INSERT INTO public.users (username, email, password, is_active, full_name, phone) VALUES
('user01', 'user01@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '张三', '13800138001'),
('user02', 'user02@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '李四', '13800138002'),
('user03', 'user03@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '王五', '13800138003'),
('user04', 'user04@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '赵六', '13800138004'),
('user05', 'user05@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '孙七', '13800138005'),
('user06', 'user06@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '周八', '13800138006'),
('user07', 'user07@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '吴九', '13800138007'),
('user08', 'user08@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '郑十', '13800138008'),
('user09', 'user09@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '冯十一', '13800138009'),
('user10', 'user10@example.com', 'scrypt:32768:8:1$2FyB7f1MVeFaGJrI$e4bbbe286cf08fe2b4fcf7a39d90dc2f0515d0ffcf197d5e933ebc55b99f714f7ff017e7b4626775b380a660cbe39deb714b770fe8b9ee9079d64ca48805820b', true, '陈十二', '13800138010')
ON CONFLICT (username) DO NOTHING;

-- 5. 为新用户分配 '普通用户' 角色
INSERT INTO public.user_roles (user_id, role_id)
SELECT
    u.id,
    (SELECT id FROM public.roles WHERE code = 'user')
FROM public.users u
WHERE u.username LIKE 'user%'
ON CONFLICT (user_id, role_id) DO NOTHING;

-- 6. 额外订单和订单项
DO $$
DECLARE
    order_id UUID;
    user_id UUID;
    product_id_1 UUID;
    product_price_1 NUMERIC(10, 2);
    product_id_2 UUID;
    product_price_2 NUMERIC(10, 2);
    order_status VARCHAR(50);
    statuses VARCHAR[] := ARRAY['completed', 'shipped', 'pending', 'cancelled'];
BEGIN
    FOR i IN 1..15 LOOP
        -- 随机选择一个用户
        SELECT id INTO user_id FROM users ORDER BY random() LIMIT 1;
        
        -- 随机选择两个不同的商品
        SELECT id, price INTO product_id_1, product_price_1 FROM products ORDER BY random() LIMIT 1;
        SELECT id, price INTO product_id_2, product_price_2 FROM products WHERE id != product_id_1 ORDER BY random() LIMIT 1;
        
        -- 随机选择一个订单状态
        order_status := statuses[1 + floor(random() * 4)];

        -- 插入订单
        INSERT INTO public.orders (user_id, order_number, total_amount, status, shipping_address)
        VALUES (
            user_id,
            (EXTRACT(EPOCH FROM CURRENT_TIMESTAMP) * 1000000)::bigint + i,
            product_price_1 * 1 + product_price_2 * 2, -- 假设第一个商品买1件，第二个买2件
            order_status,
            '地址 ' || i
        ) RETURNING id INTO order_id;

        -- 插入订单项1
        INSERT INTO public.order_items (order_id, product_id, quantity, unit_price, subtotal)
        VALUES (order_id, product_id_1, 1, product_price_1, product_price_1 * 1);

        -- 插入订单项2
        INSERT INTO public.order_items (order_id, product_id, quantity, unit_price, subtotal)
        VALUES (order_id, product_id_2, 2, product_price_2, product_price_2 * 2);
    END LOOP;
END $$;


-- =====================================================================
--  脚本结束
-- =====================================================================

-- 为操作日志表创建索引
CREATE INDEX IF NOT EXISTS idx_operation_logs_operator_id ON public.operation_logs(operator_id);
CREATE INDEX IF NOT EXISTS idx_operation_logs_module ON public.operation_logs(module);
CREATE INDEX IF NOT EXISTS idx_operation_logs_action ON public.operation_logs(action);
CREATE INDEX IF NOT EXISTS idx_operation_logs_resource_type ON public.operation_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_operation_logs_resource_id ON public.operation_logs(resource_id);
CREATE INDEX IF NOT EXISTS idx_operation_logs_status ON public.operation_logs(status);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at ON public.operation_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_operation_logs_operator_username ON public.operation_logs(operator_username);
CREATE INDEX IF NOT EXISTS idx_operation_logs_module_action ON public.operation_logs(module, action);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created_at_desc ON public.operation_logs(created_at DESC);