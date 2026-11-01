# backend/models/operation_log.py

import json

from extensions import db, db_session
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class OperationLog(db.Model):  # type: ignore
    """
    操作日志模型，记录系统中所有重要的操作行为。
    适用于用户管理、角色管理、权限管理、订单管理、商品管理等模块。
    """
    __tablename__ = 'operation_logs'

    # --- 基础字段 ---
    id = Column(BigInteger, primary_key=True)  # 主键ID
    
    # --- 操作者信息 ---
    operator_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)  # 操作者ID，允许为空（系统操作）
    operator_username = Column(String(50), nullable=True)  # 操作者用户名（冗余字段，防止用户删除后无法追溯）
    operator_name = Column(String(100), nullable=True)  # 操作者真实姓名（冗余字段）
    
    # --- 操作信息 ---
    module = Column(String(50), nullable=False)  # 操作模块（user, role, permission, order, product）
    action = Column(String(50), nullable=False)  # 操作动作（create, update, delete, login, logout, export, import等）
    resource_type = Column(String(50), nullable=False)  # 资源类型（User, Role, Permission, Order, Product等）
    resource_id = Column(String(100), nullable=True)  # 资源ID（可能是数字ID或字符串标识）
    resource_name = Column(String(200), nullable=True)  # 资源名称（用户名、角色名、订单号等）
    
    # --- 操作内容 ---
    description = Column(Text, nullable=False)  # 操作描述（人类可读）
    old_values = Column(Text, nullable=True)  # 操作前的值（JSON格式）
    new_values = Column(Text, nullable=True)  # 操作后的值（JSON格式）
    
    # --- 请求信息 ---
    ip_address = Column(String(45), nullable=True)  # 操作者IP地址（支持IPv6）
    user_agent = Column(Text, nullable=True)  # 用户代理信息
    request_method = Column(String(10), nullable=True)  # HTTP方法（GET, POST, PUT, DELETE等）
    request_url = Column(Text, nullable=True)  # 请求URL
    
    # --- 操作结果 ---
    status = Column(String(20), nullable=False, default='success')  # 操作状态（success, failed, warning）
    error_message = Column(Text, nullable=True)  # 错误信息（操作失败时）
    
    # --- 时间信息 ---
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 操作时间
    
    # --- 关系定义 ---
    operator = relationship('User', foreign_keys=[operator_id])
    
    def __repr__(self):
        return f'<OperationLog {self.operator_username} {self.action} {self.resource_type}>'
    
    def to_dict(self):
        """转换为字典格式，方便API返回"""
        return {
            'id': self.id,
            'operator_id': self.operator_id,
            'operator_username': self.operator_username,
            'operator_name': self.operator_name,
            'module': self.module,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'description': self.description,
            'old_values': json.loads(self.old_values) if self.old_values else None,
            'new_values': json.loads(self.new_values) if self.new_values else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_method': self.request_method,
            'request_url': self.request_url,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def create_log(operator_id=None, operator_username=None, operator_name=None,
                   module=None, action=None, resource_type=None, resource_id=None,
                   resource_name=None, description=None, old_values=None, new_values=None,
                   ip_address=None, user_agent=None, request_method=None, request_url=None,
                   status='success', error_message=None):
        """
        创建操作日志的静态方法
        
        Args:
            operator_id: 操作者ID
            operator_username: 操作者用户名
            operator_name: 操作者真实姓名
            module: 模块名称
            action: 操作动作
            resource_type: 资源类型
            resource_id: 资源ID
            resource_name: 资源名称
            description: 操作描述
            old_values: 操作前的值（字典）
            new_values: 操作后的值（字典）
            ip_address: IP地址
            user_agent: 用户代理
            request_method: 请求方法
            request_url: 请求URL
            status: 操作状态
            error_message: 错误信息
        
        Returns:
            OperationLog: 创建的日志记录
        """
        log = OperationLog(
            operator_id=operator_id,
            operator_username=operator_username,
            operator_name=operator_name,
            module=module,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            resource_name=resource_name,
            description=description,
            old_values=json.dumps(old_values, ensure_ascii=False, default=str) if old_values else None,
            new_values=json.dumps(new_values, ensure_ascii=False, default=str) if new_values else None,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_url=request_url,
            status=status,
            error_message=error_message
        )
        
        try:
            db_session.add(log)
            db_session.commit()
            return log
        except Exception as e:
            db_session.rollback()
            print(f"创建操作日志失败: {str(e)}")
            return None


class LogModule:
    """日志模块常量"""
    USER = 'user'
    ROLE = 'role'
    PERMISSION = 'permission'
    ORDER = 'order'
    PRODUCT = 'product'
    AUTH = 'auth'
    SYSTEM = 'system'


class LogAction:
    """日志操作常量"""
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    VIEW = 'view'
    LOGIN = 'login'
    LOGOUT = 'logout'
    EXPORT = 'export'
    IMPORT = 'import'
    BATCH_DELETE = 'batch_delete'
    BATCH_UPDATE = 'batch_update'
    ASSIGN_ROLE = 'assign_role'
    REMOVE_ROLE = 'remove_role'
    ASSIGN_PERMISSION = 'assign_permission'
    REMOVE_PERMISSION = 'remove_permission'
    CHANGE_PASSWORD = 'change_password'
    RESET_PASSWORD = 'reset_password'
    ACTIVATE = 'activate'
    DEACTIVATE = 'deactivate'
    CANCEL_ORDER = 'cancel_order'
    CONFIRM_ORDER = 'confirm_order'
    SHIP_ORDER = 'ship_order'
    COMPLETE_ORDER = 'complete_order'
    REFUND_ORDER = 'refund_order'
    ADJUST_STOCK = 'adjust_stock'


class LogStatus:
    """日志状态常量"""
    SUCCESS = 'success'
    FAILED = 'failed'
    WARNING = 'warning'