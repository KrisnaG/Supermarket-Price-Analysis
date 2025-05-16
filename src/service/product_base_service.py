from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx

from src.models.product import Product


class ProductBaseService(ABC):
    """Abstract base class for product services."""
    has_been_redirected = False

    @property
    @abstractmethod
    def _store_name(self) -> str:
        """Name of the store"""
        pass

    @property
    @abstractmethod
    def _product_url(self) -> str:
        """Base URL for product endpoints"""
        pass

    @abstractmethod
    def _extract_search_results(self, search_result: str) -> Optional[Dict[str, Any]]:
        """
        Extract search results from the response.
        :param search_result: The search result string
        :returns: Dictionary containing product details or None if not found
        """
        pass

    @abstractmethod
    def _map_product_data(self, product_data: Dict[str, Any], stockcode: str, today: str) -> Product:
        """
        Map product data to the Product model.
        :param product_data: Dictionary containing product data
        :param stockcode: The product's ID/stockcode
        :param today: Today's date in YYYY-MM-DD format
        :returns: Product object
        """
        pass

    def fetch_product(self, product_id: str, url: str = None) -> Optional[Dict[str, Any]]:
        """
        Search for a product by its ID and return its details.
        :param product_id: The product's ID/stockcode
        :param url: Optional URL to fetch the product from
        :returns: Dictionary containing product details or None if not found
        """
        if url is None:
            url = f"{self._product_url}/{product_id}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
                          "Chrome/58.0.3029.110"
                          "Safari/537.3",
        }

        try:
            result = httpx.get(url, headers=headers, timeout=30.0)

            # 200 - OK | 308 - Permanent Redirect
            if result.status_code != 200 and result.status_code != 308:
                result.raise_for_status()

            # Handle the 308 Permanent Redirect
            if result.status_code == 308 and not self.has_been_redirected:
                self.has_been_redirected = True
                # Handle the 308 Permanent Redirect
                new_url = result.headers.get('Location')
                if new_url:
                    return self.fetch_product(product_id, new_url)

            self.has_been_redirected = False
            decoded_str = result.content.decode('utf-8', errors='ignore')
            return self._extract_search_results(decoded_str)

        except httpx.RequestError as e:
            print(f"Error fetching product {product_id}: {str(e)}")
            return None

    def get_products_by_stockcodes(self, stockcodes: List[str]) -> List[Product]:
        """
        Process products and fetch their details.
        :param stockcodes: List of product stockcodes to process
        :returns: List of dictionaries containing product details
        """
        today = datetime.now().strftime('%Y-%m-%d')
        rows = []

        for stockcode in stockcodes:
            product_data = self.fetch_product(product_id=stockcode)
            if product_data:
                row = self._map_product_data(product_data, stockcode, today)
                rows.append(row)
            else:
                raise ValueError(f"Product with stockcode {stockcode} not found in {self._store_name}.")

        return rows

    def get_product_by_stockcode(self, stockcode: str) -> Product:
        """
        Get product details by stockcode.
        :param stockcode: The product's ID/stockcode
        :returns: Product if found
        """
        product = self.get_products_by_stockcodes([stockcode])[0]
        if product:
            return product
        raise ValueError(f"Product with stockcode {stockcode} not found in {self._store_name}.")
