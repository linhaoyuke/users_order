from extensions import ma
from marshmallow import fields
from models.product import Product

class ProductSchema(ma.SQLAlchemyAutoSchema):
    id = fields.UUID(dump_only=True)

    class Meta:
        model = Product
        load_instance = True
        include_fk = True
        dump_only_fields = ('initial_stock',)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
