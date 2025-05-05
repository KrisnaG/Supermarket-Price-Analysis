from datetime import datetime

from src.service.product_base_service import ProductBaseService


class WoolworthsService(ProductBaseService):
    """
    WoolworthsService is a subclass of ProductBaseService that provides
    functionality to search for products on the Woolworths website.
    """

    @property
    def _product_url(self) -> str:
        return "https://www.woolworths.com.au/shop/productdetails"

    def get_product_details(self, products: list) -> list:
        """Process products and fetch their details."""
        today = datetime.now().strftime('%Y%m%d')
        rows = []

        for product in products:
            stockcode = product["Stockcode"]
            product_data = self.search_product(stockcode)

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
