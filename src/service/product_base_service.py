from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import httpx
import json
import re


class ProductBaseService(ABC):
    """Abstract base class for product services."""

    @property
    @abstractmethod
    def _product_url(self) -> str:
        """Base URL for product endpoints"""
        pass

    def search_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Search for a product by its ID and return its details.
        :param product_id: The product's ID/stockcode
        :returns: Dictionary containing product details or None if not found
        """
        url = f"{self._product_url}/{product_id}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          "AppleWebKit/537.36 (KHTML, like Gecko)"
                          "Chrome/58.0.3029.110"
                          "Safari/537.3",
        }

        try:
            result = httpx.get(url, headers=headers, timeout=30.0)
            result.raise_for_status()
            decoded_str = result.content.decode('utf-8', errors='ignore')

            # TODO: This will not apply to coles
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                              decoded_str, re.DOTALL)

            if match:
                json_text = match.group(1)
                data = json.loads(json_text)
                return data["props"]["pageProps"]["pdDetails"]
            else:
                print(f"Could not extract JSON from response for product {product_id}")
                return None

        except (httpx.RequestError, json.JSONDecodeError, KeyError) as e:
            print(f"Error fetching product {product_id}: {str(e)}")
            return None
