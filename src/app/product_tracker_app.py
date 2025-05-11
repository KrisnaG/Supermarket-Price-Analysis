import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, messagebox, Message
from tktooltip import ToolTip

from src.repository.product_repository import ProductRepository
from src.service.product_coordinator_service import ProductCoordinatorService
from src.tools.csv_tools import save_products_to_csv


class ProductTrackerApp(tk.Tk):
    _number_of_main_components = 6

    def __init__(self, size: tuple = (2000, 1200)):
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

        show_price_history_button = ttk.Button(btn_frame, text="Price History", command=self.show_price_graph)
        show_price_history_button.pack(side="left", padx=5)
        ToolTip(show_price_history_button, msg="Show price history of products", x_offset=25, y_offset=25)

        show_product_table_button = ttk.Button(btn_frame, text="Product Table", command=self.show_product_table)
        show_product_table_button.pack(side="left", padx=5)
        ToolTip(show_product_table_button, msg="Show all products in a table", x_offset=25, y_offset=25)

        add_product_button = ttk.Button(btn_frame, text="Add Product", command=self.add_new_product)
        add_product_button.pack(side="left", padx=5)
        ToolTip(add_product_button, msg="Add a new product to the Database", x_offset=25, y_offset=25)

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
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Success", message)

    def show_price_graph(self):
        """Show a graph of product prices over time."""
        self.destroy_non_main_components()

        all_products = self.product_repository.get_all_products()
        data = {
            "date": [product.date for product in all_products],
            "product_name": [product.product_name for product in all_products],
            "price": [product.price for product in all_products],
        }
        df = pd.DataFrame(data)
        pivot = df.pivot(index='date', columns='product_name', values='price')

        fig, ax = plt.subplots(figsize=(10, 6))
        pivot.plot(ax=ax, title="Product Price History", marker='o')
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.grid(True)
        fig.autofmt_xdate()
        plot_frame = ttk.Frame(self)
        plot_frame.pack(fill='both', pady=10, expand=True)

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show_product_table(self):
        """Show a table of all products in the database."""
        self.destroy_non_main_components()

        all_products = self.product_repository.get_all_products()

        style = ttk.Style()
        style.configure("Treeview", rowheight=40)
        style.configure("Treeview.Heading", anchor="center")

        # Create a frame to hold the table and scrollbars
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create scrollbars
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(frame, orient="horizontal")

        # Create the table with scrollbar configurations
        table = ttk.Treeview(frame, columns=("Date", "ProductName", "Price", "Store"), show="headings",
                             yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Configure scrollbars
        v_scrollbar.config(command=table.yview)
        h_scrollbar.config(command=table.xview)

        # Configure column widths and alignments
        column_widths = {
            "Date": 100,
            "ProductName": 400,
            "Price": 100,
            "Store": 150
        }

        for column in ("Date", "ProductName", "Price", "Store"):
            table.heading(column, text=column, command=lambda _col=column: sort_table(_col, False))
            table.column(column, width=column_widths[column], anchor="center")

        def sort_table(col, reverse):
            """Sort the table by the given column."""
            data = [(table.set(child, col), child) for child in table.get_children("")]
            data.sort(reverse=reverse, key=lambda x: x[0])
            for index, (_, child) in enumerate(data):
                table.move(child, "", index)
            table.heading(col, command=lambda: sort_table(col, not reverse))

        # Pack scrollbars and table
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        table.pack(side="left", fill="both", expand=True)

        for product in all_products:
            table.insert("", "end", values=(product.date, product.product_name, product.price,
                                            product.store))

    def add_new_product(self):
        """Open a new window to add a new product."""
        self.destroy_non_main_components()
        # Create a new window
        add_product_frame = ttk.Frame(self)
        add_product_frame.pack(pady=10)
        add_product_label = ttk.Label(add_product_frame, text="Add a new product")
        add_product_label.pack()

        # Create entry fields for stockcode
        stockcode_frame = ttk.Frame(add_product_frame)
        stockcode_frame.pack(pady=10)
        stockcode_label = ttk.Label(stockcode_frame, text="Stockcode:")
        stockcode_label.pack(side="left", padx=(0, 5))
        stockcode_entry = ttk.Entry(stockcode_frame)
        stockcode_entry.pack(side="left")
        stockcode_entry.focus()

        # Create frame for store label and menu
        store_frame = ttk.Frame(add_product_frame)
        store_frame.pack(pady=10)
        store_label = ttk.Label(store_frame, text="Store:")
        store_label.pack(side="left", padx=(5, 10))

        store_var = tk.StringVar()
        store_var.set(list(self.product_coordinator.services.keys())[0])
        store_menu = ttk.OptionMenu(store_frame,
                                    store_var,
                                    store_var.get(),
                                    *list(self.product_coordinator.services.keys()))
        store_menu.pack(side="left", padx=(5, 10))

        # Find product button
        find_product_button = ttk.Button(add_product_frame, text="Find Product",
                                        command=lambda: self.find_product(stockcode_entry.get(), store_var.get(),
                                                                          add_product_frame))
        find_product_button.pack(pady=20)

    def find_product(self, stockcode: str, store: str, store_frame: ttk.Frame) -> None:
        """
        Find a product.
        :param stockcode: The product's ID/stockcode
        :param store: The store name
        :param store_frame: The frame to display the product details
        """
        if not stockcode.strip():
            messagebox.showerror("Error", "Stockcode cannot be empty")
            return
        try:
            product = self.product_coordinator.get_product_by_stockcode(stockcode=stockcode, store=store)

            # Create result frame and destroy any existing one
            for widget in store_frame.winfo_children():
                if isinstance(widget, ttk.Frame) and widget.winfo_name() == 'result_frame':
                    widget.destroy()

            result_frame = ttk.Frame(store_frame, name='result_frame')
            result_frame.pack(pady=20)

            # Display product details
            details = [
                f"Name: {product.product_name}",
                f"Price: ${product.price}",
                f"Store: {product.store}",
                f"Package Size: {product.package_size}",
                f"On Special: {'Yes' if product.is_on_special else 'No'}",
                f"Was Price: ${product.was_price if product.was_price else 'N/A'}"
            ]

            for detail in details:
                ttk.Label(result_frame, text=detail).pack(anchor='w')

            # Add save button
            save_button = ttk.Button(
                result_frame,
                text="Save to Database",
                command=lambda: self.save_product_to_db(product)
            )
            save_button.pack(pady=10)

        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

    def save_product_to_db(self, product) -> None:
        """Save the product to the database."""
        try:
            self.product_repository.save_product(product)
            messagebox.showinfo("Success", "Product saved to database successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {str(e)}")

    def destroy_non_main_components(self):
        """Destroy all components that are not the main components."""
        for widget in self.winfo_children()[self._number_of_main_components:]:
            widget.destroy()
