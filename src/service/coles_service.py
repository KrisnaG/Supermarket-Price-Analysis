from src.service.product_base_service import ProductBaseService


class ColesService(ProductBaseService):
    """"""
    @property
    def _product_url(self) -> str:
        return "https://www.coles.com.au/product"
