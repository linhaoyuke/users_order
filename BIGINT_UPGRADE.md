# 数据库 BigInt 升级说明

## 概述

本次更新将数据库中所有表的自增ID字段从 `INTEGER` (32位) 升级为 `BIGINT` (64位)，以支持更大的数据量。

## 修改的文件

### 1. 模型文件
- `backend/models/user.py` - 用户模型
- `backend/models/role.py` - 角色模型  
- `backend/models/permission.py` - 权限模型
- `backend/models/product.py` - 商品模型
- `backend/models/order.py` - 订单模型
- `backend/models/operation_log.py` - 操作日志模型

### 2. 数据库脚本
- `init_db.sql` - 数据库初始化脚本（新建数据库使用）
- `backend/sql/create_operation_logs.sql` - 操作日志表创建脚本
- `upgrade_to_bigint.sql` - 现有数据库升级脚本

## 影响的表和字段

### 主键字段 (SERIAL → BIGSERIAL)
- `permissions.id`
- `roles.id`
- `users.id`
- `products.id`
- `orders.id`
- `order_items.id`
- `operation_logs.id`

### 外键字段 (INTEGER → BIGINT)
- `user_roles.user_id`
- `user_roles.role_id`
- `role_permissions.role_id`
- `role_permissions.permission_id`
- `orders.user_id`
- `order_items.order_id`
- `order_items.product_id`
- `operation_logs.operator_id`

## 数据容量对比

| 类型 | 范围 | 最大值 |
|------|------|--------|
| INTEGER (32位) | -2³¹ 到 2³¹-1 | 2,147,483,647 (约21亿) |
| BIGINT (64位) | -2⁶³ 到 2⁶³-1 | 9,223,372,036,854,775,807 (约922万万亿) |

## 部署说明

### 新数据库部署
直接执行更新后的 `init_db.sql` 脚本即可。

### 现有数据库升级

1. **备份数据库**（重要！）
   ```bash
   pg_dump -h localhost -U your_username -d your_database > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **执行升级脚本**
   ```bash
   psql -h localhost -U your_username -d your_database -f upgrade_to_bigint.sql
   ```

3. **验证升级结果**
   脚本会自动输出所有表的字段类型，确认都已升级为 BIGINT。

### 注意事项

1. **性能影响**：
   - BIGINT 占用更多存储空间（8字节 vs 4字节）
   - 对于大多数应用场景，性能影响微乎其微
   - 索引大小会略微增加

2. **兼容性**：
   - Python 的 SQLAlchemy 能够无缝处理 BIGINT
   - 前端 JavaScript 中的数字精度问题（超过 Number.MAX_SAFE_INTEGER 时需要注意）

3. **回滚**：
   - 如果需要回滚，请使用备份恢复
   - 不建议将 BIGINT 降级为 INTEGER（可能丢失数据）

## 验证步骤

升级完成后，可以通过以下 SQL 验证：

```sql
-- 检查所有ID字段的数据类型
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND (column_name LIKE '%_id' OR column_name = 'id')
AND table_name IN ('permissions', 'roles', 'users', 'products', 'orders', 'order_items', 'user_roles', 'role_permissions', 'operation_logs')
ORDER BY table_name, column_name;
```

所有 ID 相关字段应该显示为 `bigint` 类型。

## 联系方式

如有问题，请联系开发团队。