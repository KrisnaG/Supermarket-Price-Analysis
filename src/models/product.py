from peewee import Model, FloatField, CharField, BooleanField


class Product(Model):
    date = CharField()
    stockcode = CharField()
    product_name = CharField()
    price = FloatField()
    is_on_special = BooleanField()
    is_half_price = BooleanField()
    was_price = FloatField()
    savings_amount = FloatField()
    package_size = CharField()
    unit_weight_in_grams = FloatField()
    cup_price = FloatField()
    cup_measure = CharField()
    cup_string = CharField()
    store = CharField()
