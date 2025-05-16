import os
from typing import List, Dict

from peewee import SqliteDatabase
from playhouse.shortcuts import model_to_dict
from src.models.product import Product
from src.tools.path_tools import get_app_root


class ProductRepository:
    """Repository to manage the Product model with SQLite."""

    def __init__(self):
        db_name = os.path.join(get_app_root(), "resources/database/products.db")
        self.database = SqliteDatabase(db_name)
        self._initialize_database()

    def _initialize_database(self):
        """Bind the Product model to the database and create tables."""
        self.database.bind([Product])
        self.database.connect()
        self.database.create_tables([Product], safe=True)

    def save_product(self, product: Product):
        """
        Save a product to the database.
        :param product: Product instance containing product details.
        """
        with self.database.atomic():
            Product.get_or_create(
                date=product.date,
                stockcode=product.stockcode,
                store=product.store,
                defaults=model_to_dict(product, exclude=[Product.id])
            )

    @staticmethod
    def get_all_stockcodes_by_store() -> Dict[str, List[str]]:
        """
        Retrieve all unique stock codes grouped by store from the Product table.
        :returns: Dictionary with store names as keys and lists of unique stock codes as values.
        """
        query = Product.select(Product.store, Product.stockcode).distinct()
        store_stockcodes = {}

        for product in query:
            store_stockcodes.setdefault(product.store, []).append(product.stockcode)

        return store_stockcodes

    @staticmethod
    def get_all_products() -> List[Product]:
        """
        Retrieve all products from the database.
        :returns: List of Product instances.
        """
        return list(Product.select())

    def close(self):
        """Close the database connection."""
        self.database.close()
