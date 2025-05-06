import os
from typing import List

import pandas as pd

from src.models.product import Product


def save_products_to_csv(products: List[Product], output_path: str) -> None:
    """Save processed data to CSV file."""
    # Convert Peewee models to dictionaries
    product_dicts = [product.__data__ for product in products]
    df_new = pd.DataFrame(product_dicts)

    if os.path.exists(output_path):
        df_new.to_csv(output_path, mode='a', header=False, index=False)
    else:
        df_new.to_csv(output_path, mode='w', header=True, index=False)
    print(f"Output saved to {output_path}")