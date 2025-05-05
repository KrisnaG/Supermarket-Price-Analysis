from peewee import Model, FloatField, CharField, DateField, BooleanField


class Product(Model):
    date = DateField()
    stockcode = CharField()
    product_name = CharField()
    price = FloatField()
    is_on_special = BooleanField()
    is_half_price = BooleanField()
    was_price = FloatField()
    savings_amount = FloatField()
    cup_price = FloatField()
    cup_measure = CharField()
    cup_string = CharField()
    store = CharField()

    class Meta:
        database = db
