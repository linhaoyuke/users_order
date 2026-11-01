# backend/models/order.py

import uuid
from extensions import db
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Order(db.Model):  # type: ignore
    """
    订单模型，代表一个完整的订单信息。
    """
    __tablename__ = 'orders'  # 定义在数据库中的表名

    # --- 字段定义 ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())  # 主键ID (UUID)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)  # 外键，关联到用户表的id
    order_number = Column(BigInteger, unique=True, nullable=False)  # 订单号，唯一且不为空
    total_amount = Column(Numeric(10, 2), nullable=False)  # 订单总金额，使用Numeric类型以保证精度
    
    # 订单状态，例如: pending_payment(待支付), processing(处理中), shipped(已发货), completed(已完成), cancelled(已取消)
    status = Column(String(20), nullable=False, default='pending_payment')
    
    # 支付状态，例如: unpaid(未支付), paid(已支付), refunded(已退款)
    payment_status = Column(String(20), nullable=False, default='unpaid')
    
    shipping_address = Column(Text)  # 收货地址
    created_at = Column(DateTime, server_default=func.now())  # 创建时间
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  # 更新时间

    # --- 关系定义 ---
    # 与OrderItem模型的一对多关系
    # backref='order' 使得在OrderItem模型中可以通过 .order 访问所属的订单
    # lazy='select' 意味着在访问order.items时会发一条新的SQL查询来加载订单项
    # cascade='all, delete-orphan' 级联操作，当删除一个Order时，所有关联的OrderItem也会被删除
    items = relationship('OrderItem', backref='order', lazy='select', cascade='all, delete-orphan')
    
    # user 的关系已通过 User 模型中的 backref='user' 自动建立，这里无需重复定义

class OrderItem(db.Model):  # type: ignore
    """
    订单项模型，代表订单中的一个具体商品。
    """
    __tablename__ = 'order_items'  # 定义在数据库中的表名

    # --- 字段定义 ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=func.gen_random_uuid())  # 主键ID (UUID)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)  # 外键，关联到订单表的id (UUID)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id', ondelete='RESTRICT'), nullable=False) # 外键，关联到商品表的id (UUID)
    quantity = Column(Integer, nullable=False)  # 商品数量
    unit_price = Column(Numeric(10, 2), nullable=False)  # 商品单价 (下单时从商品表快照)
    subtotal = Column(Numeric(10, 2), nullable=False)  # 小计金额 (quantity * unit_price)

    # --- 关系定义 ---
    product = relationship('Product')