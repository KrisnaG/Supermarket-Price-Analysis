import os

import pandas as pd


def save_to_csv(data: list, output_path: str) -> None:
    """Save processed data to CSV file."""
    df_new = pd.DataFrame(data)

    if os.path.exists(output_path):
        df_new.to_csv(output_path, mode='a', header=False, index=False)
    else:
        df_new.to_csv(output_path, mode='w', header=True, index=False)
    print(f"Output saved to {output_path}")
