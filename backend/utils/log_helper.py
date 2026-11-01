# backend/utils/log_helper.py

from functools import wraps

from flask import request, g
from models.operation_log import OperationLog, LogModule, LogAction, LogStatus
from models.user import User


class LogHelper:
    """操作日志助手类"""
    
    @staticmethod
    def get_request_info():
        """获取请求信息"""
        return {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'request_method': request.method,
            'request_url': request.url
        }
    
    @staticmethod
    def get_current_user_info():
        """获取当前用户信息"""
        current_user = getattr(g, 'current_user', None)
        if current_user:
            return {
                'operator_id': current_user.id,
                'operator_username': current_user.username,
                'operator_name': current_user.full_name
            }
        return {
            'operator_id': None,
            'operator_username': '系统',
            'operator_name': '系统操作'
        }
    
    @staticmethod
    def log_user_operation(action, user_data=None, old_data=None, resource_id=None, description=None, status=LogStatus.SUCCESS, error_message=None):
        """记录用户管理操作日志"""
        user_info = LogHelper.get_current_user_info()
        request_info = LogHelper.get_request_info()
        
        # 构建描述
        if not description:
            action_desc = {
                LogAction.CREATE: "创建用户",
                LogAction.UPDATE: "更新用户",
                LogAction.DELETE: "删除用户",
                LogAction.ACTIVATE: "激活用户",
                LogAction.DEACTIVATE: "停用用户",
                LogAction.ASSIGN_ROLE: "分配角色",
                LogAction.REMOVE_ROLE: "移除角色",
                LogAction.CHANGE_PASSWORD: "修改密码",
                LogAction.RESET_PASSWORD: "重置密码"
            }
            resource_name = user_data.get('username') if user_data else (old_data.get('username') if old_data else str(resource_id))
            description = f"{action_desc.get(action, action)} - {resource_name}"
        
        return OperationLog.create_log(
            module=LogModule.USER,
            action=action,
            resource_type='User',
            resource_id=resource_id,
            resource_name=user_data.get('username') if user_data else None,
            description=description,
            old_values=old_data,
            new_values=user_data,
            status=status,
            error_message=error_message,
            **user_info,
            **request_info
        )
    
    @staticmethod
    def log_role_operation(action, role_data=None, old_data=None, resource_id=None, description=None, status=LogStatus.SUCCESS, error_message=None):
        """记录角色管理操作日志"""
        user_info = LogHelper.get_current_user_info()
        request_info = LogHelper.get_request_info()
        
        if not description:
            action_desc = {
                LogAction.CREATE: "创建角色",
                LogAction.UPDATE: "更新角色",
                LogAction.DELETE: "删除角色",
                LogAction.ASSIGN_PERMISSION: "分配权限",
                LogAction.REMOVE_PERMISSION: "移除权限"
            }
            resource_name = role_data.get('name') if role_data else (old_data.get('name') if old_data else str(resource_id))
            description = f"{action_desc.get(action, action)} - {resource_name}"
        
        return OperationLog.create_log(
            module=LogModule.ROLE,
            action=action,
            resource_type='Role',
            resource_id=resource_id,
            resource_name=role_data.get('name') if role_data else None,
            description=description,
            old_values=old_data,
            new_values=role_data,
            status=status,
            error_message=error_message,
            **user_info,
            **request_info
        )
    
    @staticmethod
    def log_permission_operation(action, permission_data=None, old_data=None, resource_id=None, description=None, status=LogStatus.SUCCESS, error_message=None):
        """记录权限管理操作日志"""
        user_info = LogHelper.get_current_user_info()
        request_info = LogHelper.get_request_info()
        
        if not description:
            action_desc = {
                LogAction.CREATE: "创建权限",
                LogAction.UPDATE: "更新权限",
                LogAction.DELETE: "删除权限"
            }
            resource_name = permission_data.get('name') if permission_data else (old_data.get('name') if old_data else str(resource_id))
            description = f"{action_desc.get(action, action)} - {resource_name}"
        
        return OperationLog.create_log(
            module=LogModule.PERMISSION,
            action=action,
            resource_type='Permission',
            resource_id=resource_id,
            resource_name=permission_data.get('name') if permission_data else None,
            description=description,
            old_values=old_data,
            new_values=permission_data,
            status=status,
            error_message=error_message,
            **user_info,
            **request_info
        )
    
    @staticmethod
    def log_order_operation(action, order_data=None, old_data=None, resource_id=None, description=None, status=LogStatus.SUCCESS, error_message=None):
        """记录订单管理操作日志"""
        user_info = LogHelper.get_current_user_info()
        request_info = LogHelper.get_request_info()
        
        if not description:
            action_desc = {
                LogAction.CREATE: "创建订单",
                LogAction.UPDATE: "更新订单",
                LogAction.DELETE: "删除订单",
                LogAction.CANCEL_ORDER: "取消订单",
                LogAction.CONFIRM_ORDER: "确认订单",
                LogAction.SHIP_ORDER: "发货",
                LogAction.COMPLETE_ORDER: "完成订单",
                LogAction.REFUND_ORDER: "退款"
            }
            resource_name = order_data.get('order_number') if order_data else (old_data.get('order_number') if old_data else str(resource_id))
            description = f"{action_desc.get(action, action)} - {resource_name}"
        
        return OperationLog.create_log(
            module=LogModule.ORDER,
            action=action,
            resource_type='Order',
            resource_id=resource_id,
            resource_name=order_data.get('order_number') if order_data else None,
            description=description,
            old_values=old_data,
            new_values=order_data,
            status=status,
            error_message=error_message,
            **user_info,
            **request_info
        )
    
    @staticmethod
    def log_product_operation(action, product_data=None, old_data=None, resource_id=None, description=None, status=LogStatus.SUCCESS, error_message=None):
        """记录商品管理操作日志"""
        user_info = LogHelper.get_current_user_info()
        request_info = LogHelper.get_request_info()
        
        if not description:
            action_desc = {
                LogAction.CREATE: "创建商品",
                LogAction.UPDATE: "更新商品",
                LogAction.DELETE: "删除商品",
                LogAction.ADJUST_STOCK: "调整库存"
            }
            resource_name = product_data.get('name') if product_data else (old_data.get('name') if old_data else str(resource_id))
            description = f"{action_desc.get(action, action)} - {resource_name}"
        
        return OperationLog.create_log(
            module=LogModule.PRODUCT,
            action=action,
            resource_type='Product',
            resource_id=resource_id,
            resource_name=product_data.get('name') if product_data else None,
            description=description,
            old_values=old_data,
            new_values=product_data,
            status=status,
            error_message=error_message,
            **user_info,
            **request_info
        )
    
    @staticmethod
    def log_auth_operation(action, description, status=LogStatus.SUCCESS, error_message=None):
        """记录认证相关操作日志"""
        user_info = LogHelper.get_current_user_info()
        request_info = LogHelper.get_request_info()
        
        return OperationLog.create_log(
            module=LogModule.AUTH,
            action=action,
            resource_type='Auth',
            description=description,
            status=status,
            error_message=error_message,
            **user_info,
            **request_info
        )


def log_operation(module, action, resource_type=None, get_resource_info=None):
    """
    装饰器：自动记录操作日志
    
    Args:
        module: 模块名称
        action: 操作动作
        resource_type: 资源类型
        get_resource_info: 获取资源信息的函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 执行原函数
                result = func(*args, **kwargs)
                
                # 获取资源信息
                resource_info = {}
                if get_resource_info:
                    resource_info = get_resource_info(*args, **kwargs)
                
                # 记录成功日志
                user_info = LogHelper.get_current_user_info()
                request_info = LogHelper.get_request_info()
                
                OperationLog.create_log(
                    module=module,
                    action=action,
                    resource_type=resource_type or 'Unknown',
                    description=f"{action} {resource_type or 'resource'}",
                    status=LogStatus.SUCCESS,
                    **resource_info,
                    **user_info,
                    **request_info
                )
                
                return result
                
            except Exception as e:
                # 记录失败日志
                user_info = LogHelper.get_current_user_info()
                request_info = LogHelper.get_request_info()
                
                OperationLog.create_log(
                    module=module,
                    action=action,
                    resource_type=resource_type or 'Unknown',
                    description=f"{action} {resource_type or 'resource'} - 操作失败",
                    status=LogStatus.FAILED,
                    error_message=str(e),
                    **user_info,
                    **request_info
                )
                
                # 重新抛出异常
                raise e
                
        return wrapper
    return decorator