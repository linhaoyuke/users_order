from extensions import ma
from marshmallow import fields
from models.order import Order, OrderItem
from schemas.product import ProductSchema


class OrderItemSchema(ma.Schema):
    id = fields.UUID(dump_only=True)
    order_id = fields.UUID(dump_only=True)
    product_id = fields.UUID(dump_only=True)
    quantity = fields.Int()
    unit_price = fields.Decimal(as_string=True, places=2)
    subtotal = fields.Decimal(as_string=True, places=2)
    product = fields.Nested(ProductSchema, dump_only=True)

class OrderSchema(ma.Schema):
    id = fields.UUID(dump_only=True)
    order_number = fields.Str(dump_only=True)
    total_amount = fields.Decimal(as_string=True, places=2)
    status = fields.Str()
    payment_status = fields.Str()
    shipping_address = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)
    user_username = fields.Method("get_user_username", dump_only=True)
    user_full_name = fields.Method("get_user_full_name", dump_only=True)
    user_id = fields.Int(dump_only=True)

    def get_user_username(self, obj):
        return obj.user.username if obj.user else None

    def get_user_full_name(self, obj):
        return obj.user.full_name if obj.user else None

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)