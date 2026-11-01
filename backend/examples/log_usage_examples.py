# backend/examples/log_usage_examples.py

"""
操作日志使用示例
展示如何在各个模块中集成操作日志功能
"""

from models.order import Order
from models.product import Product
from models.role import Role
from models.user import User
from utils.log_helper import LogHelper, LogModule, LogAction, LogStatus, log_operation


# ==================== 用户管理操作日志示例 ====================

def create_user_example():
    """创建用户时记录日志"""
    try:
        # 创建用户的业务逻辑
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'full_name': '新用户',
            'is_active': True
        }
        
        # 假设创建用户成功，获取到user_id
        user_id = 123

        
        # 记录操作日志
        LogHelper.log_user_operation(
            action=LogAction.CREATE,
            user_data=user_data,
            resource_id=user_id,
            description=f"创建用户 - {user_data['username']}"
        )
        
    except Exception as e:
        # 记录失败日志
        LogHelper.log_user_operation(
            action=LogAction.CREATE,
            user_data=user_data,
            status=LogStatus.FAILED,
            error_message=str(e)
        )


def update_user_example():
    """更新用户时记录日志"""
    user_id = 123
    
    # 获取更新前的数据
    old_data = {
        'username': 'olduser',
        'email': 'old@example.com',
        'full_name': '旧用户名',
        'is_active': True
    }
    
    # 新数据
    new_data = {
        'username': 'olduser',
        'email': 'new@example.com',
        'full_name': '新用户名',
        'is_active': True
    }
    
    # 记录操作日志
    LogHelper.log_user_operation(
        action=LogAction.UPDATE,
        user_data=new_data,
        old_data=old_data,
        resource_id=user_id,
        description=f"更新用户信息 - {new_data['username']}"
    )


def assign_role_example():
    """分配角色时记录日志"""
    user_id = 123
    role_ids = [1, 2]
    
    # 记录角色分配日志
    LogHelper.log_user_operation(
        action=LogAction.ASSIGN_ROLE,
        user_data={'roles': role_ids},
        resource_id=user_id,
        description=f"为用户分配角色 - 角色ID: {', '.join(map(str, role_ids))}"
    )


# ==================== 订单管理操作日志示例 ====================

def create_order_example():
    """创建订单时记录日志"""
    order_data = {
        'order_number': '20241222001',
        'user_id': 123,
        'total_amount': '299.50',
        'status': 'pending_payment',
        'items': [
            {'product_id': 1, 'quantity': 2, 'unit_price': '99.00'},
            {'product_id': 2, 'quantity': 1, 'unit_price': '101.50'}
        ]
    }
    
    order_id = 456
    
    LogHelper.log_order_operation(
        action=LogAction.CREATE,
        order_data=order_data,
        resource_id=order_id,
        description=f"创建订单 - {order_data['order_number']}"
    )


def update_order_status_example():
    """更新订单状态时记录日志"""
    order_id = 456
    
    old_data = {'status': 'pending_payment', 'payment_status': 'unpaid'}
    new_data = {'status': 'processing', 'payment_status': 'paid'}
    
    LogHelper.log_order_operation(
        action=LogAction.UPDATE,
        order_data=new_data,
        old_data=old_data,
        resource_id=order_id,
        description="订单状态更新 - 已支付，处理中"
    )


def cancel_order_example():
    """取消订单时记录日志"""
    order_id = 456
    
    LogHelper.log_order_operation(
        action=LogAction.CANCEL_ORDER,
        resource_id=order_id,
        description="取消订单 - 用户申请取消"
    )


# ==================== 商品管理操作日志示例 ====================

def create_product_example():
    """创建商品时记录日志"""
    product_data = {
        'name': '新商品',
        'description': '商品描述',
        'price': '199.00',
        'stock': 100,
        'initial_stock': 100
    }
    
    product_id = 789
    
    LogHelper.log_product_operation(
        action=LogAction.CREATE,
        product_data=product_data,
        resource_id=product_id,
        description=f"创建商品 - {product_data['name']}"
    )


def adjust_stock_example():
    """调整库存时记录日志"""
    product_id = 789
    
    old_data = {'stock': 100}
    new_data = {'stock': 80}
    adjustment = -20
    
    LogHelper.log_product_operation(
        action=LogAction.ADJUST_STOCK,
        product_data=new_data,
        old_data=old_data,
        resource_id=product_id,
        description=f"调整库存 - 调整数量: {adjustment}，当前库存: {new_data['stock']}"
    )


# ==================== 使用装饰器的示例 ====================

@log_operation(
    module=LogModule.USER,
    action=LogAction.DELETE,
    resource_type='User',
    get_resource_info=lambda user_id: {
        'resource_id': user_id,
        'resource_name': f'用户{user_id}',
        'description': f'删除用户 - ID: {user_id}'
    }
)
def delete_user_with_decorator(user_id):
    """使用装饰器自动记录日志的删除用户示例"""
    # 删除用户的业务逻辑
    # User.query.filter_by(id=user_id).delete()
    pass


@log_operation(
    module=LogModule.PRODUCT,
    action=LogAction.UPDATE,
    resource_type='Product'
)
def update_product_with_decorator(product_id, product_data):
    """使用装饰器自动记录日志的更新商品示例"""
    # 更新商品的业务逻辑
    pass


# ==================== 认证相关日志示例 ====================

def login_example():
    """用户登录时记录日志"""
    username = 'admin'
    
    LogHelper.log_auth_operation(
        action=LogAction.LOGIN,
        description=f"用户登录 - {username}"
    )


def logout_example():
    """用户登出时记录日志"""
    username = 'admin'
    
    LogHelper.log_auth_operation(
        action=LogAction.LOGOUT,
        description=f"用户登出 - {username}"
    )


def failed_login_example():
    """登录失败时记录日志"""
    username = 'admin'
    
    LogHelper.log_auth_operation(
        action=LogAction.LOGIN,
        description=f"用户登录失败 - {username}",
        status=LogStatus.FAILED,
        error_message="密码错误"
    )


# ==================== 批量操作日志示例 ====================

def batch_delete_users_example():
    """批量删除用户时记录日志"""
    user_ids = [1, 2, 3, 4, 5]
    
    LogHelper.log_user_operation(
        action=LogAction.BATCH_DELETE,
        user_data={'deleted_user_ids': user_ids},
        description=f"批量删除用户 - 共{len(user_ids)}个用户",
        resource_id=','.join(map(str, user_ids))
    )


def batch_update_product_prices_example():
    """批量更新商品价格时记录日志"""
    updates = [
        {'id': 1, 'old_price': '99.00', 'new_price': '89.00'},
        {'id': 2, 'old_price': '199.00', 'new_price': '179.00'}
    ]
    
    LogHelper.log_product_operation(
        action=LogAction.BATCH_UPDATE,
        product_data={'price_updates': updates},
        description=f"批量更新商品价格 - 共{len(updates)}个商品"
    )


# ==================== 数据导入导出日志示例 ====================

def import_users_example():
    """导入用户数据时记录日志"""
    import_count = 50
    
    LogHelper.log_user_operation(
        action=LogAction.IMPORT,
        user_data={'import_count': import_count},
        description=f"导入用户数据 - 共导入{import_count}个用户"
    )


def export_orders_example():
    """导出订单数据时记录日志"""
    export_count = 1000
    date_range = '2024-01-01 到 2024-12-31'
    
    LogHelper.log_order_operation(
        action=LogAction.EXPORT,
        order_data={
            'export_count': export_count,
            'date_range': date_range
        },
        description=f"导出订单数据 - {date_range}，共{export_count}条记录"
    )


if __name__ == "__main__":
    # 运行示例
    print("操作日志使用示例")
    print("请根据实际需求在各个API接口中集成这些日志记录方法")