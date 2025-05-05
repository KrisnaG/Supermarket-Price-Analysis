import json


def load_products(input_json_path: str) -> list:
    """Load product data from JSON file."""
    with open(input_json_path, 'r') as file:
        return json.load(file)
