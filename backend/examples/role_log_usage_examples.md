# 角色管理操作日志使用示例

本文档展示了角色管理模块中操作日志的实现和使用方式。

## 实现概述

角色管理模块已经集成了完整的操作日志功能，涵盖以下操作：

1. **角色创建** - 记录新角色的创建，包括基本信息和分配的权限
2. **角色更新** - 记录角色信息的修改，包括前后数据对比
3. **角色删除** - 记录角色的删除操作
4. **权限分配** - 记录角色权限的分配和变更
5. **操作失败** - 记录验证失败、唯一性冲突等错误情况

## 日志记录内容

每个操作都会记录以下信息：

- **操作者信息**：当前用户ID、用户名、真实姓名
- **操作详情**：模块(role)、动作类型、资源信息
- **数据变更**：操作前后的数据对比（JSON格式）
- **请求信息**：IP地址、用户代理、请求方法、请求URL
- **操作结果**：成功/失败状态、错误信息
- **时间戳**：操作发生的准确时间

## 使用示例

### 1. 角色创建日志

```python
# 在 create_role() 函数中
# 成功时记录
LogHelper.log_role_operation(
    action=LogAction.CREATE,
    role_data=log_data,
    resource_id=new_role.id,
    description=f"创建角色 - {new_role.name}"
)

# 失败时记录
LogHelper.log_role_operation(
    action=LogAction.CREATE,
    role_data=json_data,
    status=LogStatus.FAILED,
    error_message="角色名已存在"
)
```

### 2. 角色更新日志

```python
# 在 update_role() 函数中
# 记录操作前后的数据对比
old_data = {
    'name': role.name,
    'code': role.code,
    'description': role.description,
    'permissions': [{'id': p.id, 'name': p.name} for p in role.permissions]
}

# 更新操作后
new_data = {
    'name': role.name,
    'code': role.code,
    'description': role.description,
    'permissions': [{'id': p.id, 'name': p.name} for p in role.permissions]
}

LogHelper.log_role_operation(
    action=LogAction.UPDATE,
    role_data=new_data,
    old_data=old_data,
    resource_id=role_id,
    description=f"更新角色信息 - {role.name}"
)
```

### 3. 权限分配日志

```python
# 在 assign_permissions_to_role() 函数中
LogHelper.log_role_operation(
    action=LogAction.ASSIGN_PERMISSION,
    role_data={
        'assigned_permissions': new_permissions,
        'permission_ids': data['permission_ids']
    },
    old_data={'permissions': old_permissions},
    resource_id=role_id,
    description=f"为角色 {role.name} 分配权限"
)
```

## 日志查询

可以通过操作日志API查询角色相关的日志：

```bash
# 获取所有角色模块的日志
GET /api/operation-logs/?module=role

# 获取特定角色的日志
GET /api/operation-logs/?module=role&resource_id=1

# 获取特定操作类型的日志
GET /api/operation-logs/?module=role&action=create

# 获取失败的操作日志
GET /api/operation-logs/?module=role&status=failed
```

## 测试验证

运行测试脚本验证日志功能：

```bash
cd backend
python test_role_logs.py
```

该脚本会执行以下测试：
1. 角色创建操作及其日志记录
2. 角色更新操作及其日志记录
3. 权限分配操作及其日志记录
4. 角色删除操作及其日志记录
5. 验证失败情况的日志记录
6. 查询和验证生成的日志记录

## 注意事项

1. **敏感数据保护**：日志中不会记录敏感信息，如密码字段
2. **数据完整性**：记录操作前后的完整数据对比，便于审计
3. **错误处理**：所有失败情况都有相应的日志记录
4. **性能考虑**：日志记录是异步操作，不影响主要业务流程
5. **存储管理**：建议定期清理旧的日志记录，避免数据库过大

## 日志数据示例

### 角色创建成功日志
```json
{
    "module": "role",
    "action": "create",
    "resource_type": "Role",
    "resource_id": "5",
    "resource_name": "测试角色",
    "description": "创建角色 - 测试角色",
    "new_values": {
        "name": "测试角色",
        "code": "TEST_ROLE",
        "description": "这是一个测试角色",
        "role_id": 5,
        "assigned_permissions": [
            {"id": 1, "name": "用户管理"},
            {"id": 2, "name": "角色管理"}
        ]
    },
    "status": "success",
    "operator_username": "admin",
    "ip_address": "127.0.0.1"
}
```

### 角色更新日志
```json
{
    "module": "role",
    "action": "update",
    "resource_type": "Role",
    "resource_id": "5",
    "resource_name": "测试角色",
    "description": "更新角色信息 - 测试角色",
    "old_values": {
        "name": "测试角色",
        "code": "TEST_ROLE",
        "description": "这是一个测试角色",
        "permissions": [{"id": 1, "name": "用户管理"}]
    },
    "new_values": {
        "name": "测试角色-已更新",
        "code": "TEST_ROLE",
        "description": "这是一个已更新的测试角色",
        "permissions": [
            {"id": 1, "name": "用户管理"},
            {"id": 2, "name": "角色管理"}
        ],
        "permissions_updated": true
    },
    "status": "success"
}
```

### 操作失败日志
```json
{
    "module": "role",
    "action": "create",
    "resource_type": "Role",
    "description": "创建角色 - ",
    "new_values": {
        "name": "管理员",
        "code": "ADMIN"
    },
    "status": "failed",
    "error_message": "角色名已存在"
}
```