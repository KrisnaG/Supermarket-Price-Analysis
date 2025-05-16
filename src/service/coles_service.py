from typing import Optional, Dict, Any

from src.models.product import Product
from src.service.product_base_service import ProductBaseService


class ColesService(ProductBaseService):
    """Coles related services."""

    @property
    def _store_name(self) -> str:
        return "Coles"

    @property
    def _product_url(self) -> str:
        # TODO - URL not confirmed
        return "https://www.coles.com.au/product"

    def _extract_search_results(self, search_result: str) -> Optional[Dict[str, Any]]:
        # TODO - Not implemented yet
        pass

    def _map_product_data(self, product_data: Dict[str, Any], stockcode: str, today: str) -> Product:
        # TODO - Not implemented yet
        pass
