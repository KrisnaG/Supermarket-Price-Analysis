from enum import Enum
from typing import Type, Dict

from src.service.product_base_service import ProductBaseService
from src.service.woolworths_service import WoolworthsService
from src.service.coles_service import ColesService


class ServiceType(Enum):
    """Enum representing different product service types."""
    WOOLWORTHS = "woolworths"
    COLES = "coles"


class ServiceFactory:
    """Factory class for creating instances of product services."""
    _services: Dict[ServiceType, Type[ProductBaseService]] = {
        ServiceType.WOOLWORTHS: WoolworthsService,
        ServiceType.COLES: ColesService,
    }

    @classmethod
    def create_service(cls, service_type: ServiceType) -> ProductBaseService:
        """
        Create a new price service instance.
        :param service_type: The type of service to create
        :return: A new instance of the requested service
        :raises ValueError: If the service type is not supported
        """
        if service_type not in cls._services:
            raise ValueError(f"Unsupported service type: {service_type}")

        return cls._services[service_type]()
