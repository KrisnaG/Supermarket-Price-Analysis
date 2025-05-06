import json
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

from src.models.product import Product
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

    def get_product_details(self, stockcodes: List[str]) -> List[Product]:
        """
        Process products and fetch their details.
        :param stockcodes: List of product stockcodes to process.
        :returns: List of dictionaries containing product details.
        """
        today = datetime.now().strftime('%Y-%m-%d')
        rows = []

        for stockcode in stockcodes:
            product_data = self.search_product(product_id=stockcode)

            if product_data:
                row = Product(
                    date=today,
                    stockcode=stockcode,
                    product_name=product_data["Product"]["Name"],
                    price=product_data["Product"]["Price"],
                    is_on_special=product_data["Product"]["IsOnSpecial"],
                    is_half_price=product_data["Product"]["IsHalfPrice"],
                    was_price=product_data["Product"]["WasPrice"],
                    savings_amount=product_data["Product"]["SavingsAmount"],
                    package_size=product_data["Product"]["PackageSize"].upper(),
                    unit_weight_in_grams=product_data["Product"]["UnitWeightInGrams"],
                    cup_price=product_data["Product"]["CupPrice"],
                    cup_measure=product_data["Product"]["CupMeasure"],
                    cup_string=product_data["Product"]["CupString"],
                    store="woolworths",
                )
                rows.append(row)

        return rows
