from src.service.service_factory import ServiceFactory, ServiceType


def main():
    input_json_path = 'resources/woolworths_products.json'
    output_csv_path = 'resources/woolworths_results.csv'
    woolworths_service = ServiceFactory.create_service(ServiceType('woolworths'))
    print(woolworths_service.search_product("888140"))


if __name__ == "__main__":
    main()
