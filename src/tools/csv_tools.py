from typing import List

import pandas as pd

from src.models.product import Product


def save_products_to_csv(products: List[Product], output_path: str) -> (bool, str):
    """Save processed data to CSV file."""
    try:
        # Convert Peewee models to dictionaries
        product_dicts = [product.__data__ for product in products]
        df_new = pd.DataFrame(product_dicts)
        df_new.to_csv(output_path, mode='w', header=True, index=False)
        return True, f"Products saved to {output_path}"
    except Exception as e:
        return False, f"An error occurred while saving to CSV: {e}"
