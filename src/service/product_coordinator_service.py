from typing import Dict, List
from src.models.product import Product
from src.service.woolworths_service import WoolworthsService
from src.service.coles_service import ColesService
from src.service.product_base_service import ProductBaseService


class ProductCoordinatorService:
    def __init__(self):
        self.services: Dict[str, ProductBaseService] = {
            "woolworths": WoolworthsService(),
            "coles": ColesService()
        }

    def update_all_products(self, product_lists: Dict[str, List[str]]) -> List[Product]:
        """
        Update products from all services.
        :param product_lists: Dictionary mapping store names to lists of stockcodes
        :returns: Combined list of updated products
        """
        all_products = []

        for store_name, service in self.services.items():
            if store_name in product_lists and product_lists[store_name]:
                store_products = service.get_product_details(product_lists[store_name])
                all_products.extend(store_products)

        return all_products