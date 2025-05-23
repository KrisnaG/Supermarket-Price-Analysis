import json
import re
from typing import Optional, Dict, Any

from src.models.product import Product
from src.service.product_base_service import ProductBaseService


class WoolworthsService(ProductBaseService):
    """Woolworths related services."""

    @property
    def _store_name(self) -> str:
        return "Woolworths"

    @property
    def _product_url(self) -> str:
        return "https://www.woolworths.com.au/shop/productdetails"

    def _extract_search_results(self, search_result: str) -> Optional[Dict[str, Any]]:
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                          search_result, re.DOTALL)

        if match:
            json_text = match.group(1)
            data = json.loads(json_text)
            return data["props"]["pageProps"]["pdDetails"]
        else:
            print("Could not find the Woolworths product details in the response.")

        return None

    def _map_product_data(self, product_data: Dict[str, Any], stockcode: str, today: str) -> Product:
        return Product(
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
            store=self._store_name,
        )
