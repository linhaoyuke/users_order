# backend/schemas/operation_log.py

from extensions import ma
from marshmallow import fields, validate
from models.operation_log import OperationLog


class OperationLogSchema(ma.SQLAlchemyAutoSchema):
    """
    操作日志Schema，用于序列化操作日志数据
    """
    # 添加自定义字段
    operator_info = fields.Method("get_operator_info", dump_only=True)
    formatted_created_at = fields.Method("get_formatted_created_at", dump_only=True)
    
    class Meta:
        model = OperationLog
        load_instance = True
        # 包含所有字段，但不包括关系字段
        exclude = ('operator',)  # 排除关系字段以避免复杂化
    
    def get_operator_info(self, obj):
        """获取操作者信息"""
        if obj.operator_name:
            return f"{obj.operator_name}({obj.operator_username})"
        elif obj.operator_username:
            return obj.operator_username
        else:
            return "系统"
    
    def get_formatted_created_at(self, obj):
        """格式化操作时间"""
        if obj.created_at:
            return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return None


class OperationLogQuerySchema(ma.Schema):
    """
    操作日志查询Schema，用于验证查询参数
    """
    # 分页参数
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))
    
    # 筛选参数
    operator_id = fields.Int()
    operator_username = fields.Str()
    module = fields.Str(validate=validate.OneOf([
        'user', 'role', 'permission', 'order', 'product', 'auth', 'system'
    ]))
    action = fields.Str()
    resource_type = fields.Str()
    resource_id = fields.Str()
    status = fields.Str(validate=validate.OneOf(['success', 'failed', 'warning']))
    
    # 时间范围参数
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    
    # 搜索关键词
    keyword = fields.Str()


# 创建schema实例
operation_log_schema = OperationLogSchema()
operation_logs_schema = OperationLogSchema(many=True)
operation_log_query_schema = OperationLogQuerySchema()