import tkinter as tk
from tkinter import ttk

from src.repository.product_repository import ProductRepository
from src.service.product_coordinator_service import ProductCoordinatorService
from src.tools.csv_tools import save_products_to_csv


class ProductTrackerApp(tk.Tk):
    def __init__(self, size: tuple = (1000, 600)):
        super().__init__()
        self.title("Product Price Tracker")
        self.geometry(f"{size[0]}x{size[1]}")
        self.minsize(size[0], size[1])
        self.create_buttons()
        # Services
        self.product_repository = ProductRepository()
        self.product_coordinator = ProductCoordinatorService()

    def run_application(self):
        """Run the main application loop."""
        self.mainloop()

    def create_buttons(self):
        """Create buttons for the main application window."""
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Update Products", command=self.update_products).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Show Price History", command=self.show_price_graph).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Show Product Table", command=self.show_product_table).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Download CSV", command=self.download_all_products_to_csv).pack(side="left", padx=5)

    def update_products(self):
        """Update products from all stores."""
        product_list = self.product_repository.get_all_stockcodes_by_store()
        today_update = self.product_coordinator.update_all_products(product_list)
        for product in today_update:
            self.product_repository.save_product(product)

    def download_all_products_to_csv(self):
        """Download all products to a CSV file."""
        all_products = self.product_repository.get_all_products()
        save_products_to_csv(all_products, "products.csv")

    def show_price_graph(self):
        pass

    def show_product_table(self):
        pass
