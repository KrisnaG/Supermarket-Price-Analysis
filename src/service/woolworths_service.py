import json
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

from src.service.product_base_service import ProductBaseService


class WoolworthsService(ProductBaseService):
    """Woolworths related services."""

    @property
    def _product_url(self) -> str:
        return "https://www.woolworths.com.au/shop/productdetails"

    def extract_search_results(self, search_result: str) -> Optional[Dict[str, Any]]:
        """
        Extract search results from the response.
        :param search_result: The search result string.
        :returns: Dictionary containing product details or None if not found.
        """
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                          search_result, re.DOTALL)

        if match:
            json_text = match.group(1)
            data = json.loads(json_text)
            return data["props"]["pageProps"]["pdDetails"]
        else:
            print(f"Could not extract JSON from response for product")

        return None

    def get_product_details(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process products and fetch their details.
        :param products: List of products to process.
        :returns: List of dictionaries containing product details.
        """
        today = datetime.now().strftime('%Y%m%d')
        rows = []

        for product in products:
            stockcode = product["Stockcode"]
            product_data = self.search_product(product_id=stockcode)

            if product_data:
                row = {
                    "Date": today,
                    "Stockcode": stockcode,
                    "Name": product_data["Product"]["Name"],
                    "Price": product_data["Product"]["Price"],
                    **product_data
                }
                rows.append(row)

        return rows
