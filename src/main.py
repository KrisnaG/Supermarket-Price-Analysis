from typing import List

from src.models.product import Product
from src.repository.product_repository import ProductRepository
from src.service.woolworths_service import WoolworthsService
from src.tools.csv_tools import save_products_to_csv


def main():
    product_repository = ProductRepository()
    product_list = product_repository.get_all_stockcodes_by_store()
    woolworths_service = WoolworthsService()
    today_update: List[Product] = woolworths_service.get_product_details(product_list["woolworths"])
    for product in today_update:
        print(f"Product: {product.product_name} - {product.price}")
        product_repository.save_product(product)
    save_products_to_csv(today_update, "products.csv")

if __name__ == "__main__":
    main()
