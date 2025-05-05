from typing import Optional, Dict, Any

from src.service.product_base_service import ProductBaseService


class ColesService(ProductBaseService):
    """Coles related services."""

    @property
    def _product_url(self) -> str:
        return "https://www.coles.com.au/product"

    def extract_search_results(self, search_result: str) -> Optional[Dict[str, Any]]:
        """
        Extract search results from the response.
        :param search_result: The search result string.
        :returns: Dictionary containing product details or None if not found.
        """
        pass
