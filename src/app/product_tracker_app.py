import tkinter as tk
from tkinter import ttk, messagebox
from tktooltip import ToolTip

from src.repository.product_repository import ProductRepository
from src.service.product_coordinator_service import ProductCoordinatorService
from src.tools.csv_tools import save_products_to_csv


class ProductTrackerApp(tk.Tk):
    def __init__(self, size: tuple = (1200, 900)):
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

        update_product_button = ttk.Button(btn_frame, text="Update Products", command=self.update_products)
        update_product_button.pack(side="left", padx=5)
        ToolTip(update_product_button, msg="Update products from all stores", x_offset=25, y_offset=25)

        show_price_history_button = ttk.Button(btn_frame, text="Show Price History", command=self.show_price_graph)
        show_price_history_button.pack(side="left", padx=5)
        ToolTip(show_price_history_button, msg="Show price history of products", x_offset=25, y_offset=25)

        show_product_table_button = ttk.Button(btn_frame, text="Show Product Table", command=self.show_product_table)
        show_product_table_button.pack(side="left", padx=5)
        ToolTip(show_product_table_button, msg="Show all products in a table", x_offset=25, y_offset=25)

        download_csv_button = ttk.Button(btn_frame, text="Download CSV", command=self.download_all_products_to_csv)
        download_csv_button.pack(side="left", padx=5)
        ToolTip(download_csv_button, msg="Download all products to a CSV file", x_offset=25, y_offset=25)

    def update_products(self):
        """Update products from all stores."""
        # Create progress bar frame and label
        progress_frame = ttk.Frame(self)
        progress_frame.pack(pady=10)
        progress_label = ttk.Label(progress_frame, text="Updating products...")
        progress_label.pack()

        progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=300)
        progress_bar.pack()

        try:
            # Get products
            progress_label.config(text="Fetching product list...")
            self.update_idletasks()
            product_list = self.product_repository.get_all_stockcodes_by_store()
            progress_bar['value'] = 25

            # Update products
            progress_label.config(text="Updating product information...")
            self.update_idletasks()
            today_update = self.product_coordinator.update_all_products(product_list)
            progress_bar['value'] = 75

            # Save products
            progress_label.config(text="Saving updated products...")
            self.update_idletasks()
            for product in today_update:
                self.product_repository.save_product(product)
            progress_bar['value'] = 100

            messagebox.showinfo("Success", "Products updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update products: {str(e)}")
        finally:
            # Clean up
            if 'progress_frame' in locals():
                progress_frame.destroy()

    def download_all_products_to_csv(self):
        """Download all products to a CSV file."""
        all_products = self.product_repository.get_all_products()
        successful, message = save_products_to_csv(all_products, "products.csv")
        if not successful:
            messagebox.showerror("Error", message, )
        else:
            messagebox.showinfo("Success", message)

    def show_price_graph(self):
        pass

    def show_product_table(self):
        all_products = self.product_repository.get_all_products()

        style = ttk.Style()
        style.configure("Treeview", rowheight=40)

        table = ttk.Treeview(self, columns=("Date", "Stockcode", "Store", "Price"), show="headings")
        table.heading("Date", text="Date")
        table.heading("Stockcode", text="Stockcode")
        table.heading("Store", text="Store")
        table.heading("Price", text="Price")

        def sort_table(col, reverse):
            """Sort the table by the given column."""
            data = [(table.set(child, col), child) for child in table.get_children("")]
            data.sort(reverse=reverse, key=lambda x: x[0])
            for index, (_, child) in enumerate(data):
                table.move(child, "", index)
            table.heading(col, command=lambda: sort_table(col, not reverse))

        for column in ("Date", "Stockcode", "Store", "Price"):
            table.heading(column, text=column, command=lambda _col=column: sort_table(_col, False))

        table.pack(fill="both", expand=True)

        for product in all_products:
            table.insert("", "end", values=(product.date, product.stockcode, product.store, product.price))
