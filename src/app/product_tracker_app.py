import math
import re
from typing import List
from httpx import HTTPStatusError

import pandas as pd
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk, messagebox
from tktooltip import ToolTip

from src.models.product import Product
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

        update_product_button = ttk.Button(btn_frame, text="Update Products", command=self.update_products_ui)
        update_product_button.pack(side="left", padx=5)
        ToolTip(update_product_button, msg="Update products from all stores", x_offset=25, y_offset=25)

        show_price_history_button = ttk.Button(btn_frame, text="Price History", command=self.show_price_graph)
        show_price_history_button.pack(side="left", padx=5)
        ToolTip(show_price_history_button, msg="Show price history of products", x_offset=25, y_offset=25)

        show_product_table_button = ttk.Button(btn_frame, text="Product Table", command=self.show_product_table)
        show_product_table_button.pack(side="left", padx=5)
        ToolTip(show_product_table_button, msg="Show all products in a table", x_offset=25, y_offset=25)

        add_new_product_button = ttk.Button(btn_frame, text="Add New Product", command=self.add_new_product)
        add_new_product_button.pack(side="left", padx=5)
        ToolTip(add_new_product_button, msg="Add a new product to the Database", x_offset=25, y_offset=25)

        add_product_entries_button = ttk.Button(btn_frame, text="Add Product Entries",
                                                command=self.add_new_entry_to_products)
        add_product_entries_button.pack(side="left", padx=5)
        ToolTip(add_product_entries_button, msg="Add entries for products", x_offset=25, y_offset=25)

        download_csv_button = ttk.Button(btn_frame, text="Download CSV", command=self.show_download_csv_ui)
        download_csv_button.pack(side="left", padx=5)
        ToolTip(download_csv_button, msg="Download all products to a CSV file", x_offset=25, y_offset=25)

    def update_products_ui(self):
        """
        Display UI for downloading all products to CSV with a user-provided filename.
        """
        self.destroy_non_main_components()

        update_product_frame = ttk.Frame(self)
        update_product_frame.pack(pady=10, fill='x')

        label = ttk.Label(update_product_frame, text="Update all products in database with todays prices")
        label.pack(padx=(10, 5))

        update_button = ttk.Button(
            update_product_frame,
            text="Update",
            command=lambda: self._update_products()
        )
        update_button.pack(side='bottom', padx=(0, 10), pady=30)

    def _update_products(self):
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

    def show_download_csv_ui(self):
        """
        Display UI for downloading all products to CSV with a user-provided filename.
        """
        self.destroy_non_main_components()

        download_frame = ttk.Frame(self)
        download_frame.pack(pady=10, fill='x')

        label = ttk.Label(download_frame, text="CSV Filename:")
        label.pack(padx=(10, 5))

        filename_entry = ttk.Entry(download_frame)
        filename_entry.insert(0, "products")
        filename_entry.pack(expand=False, padx=(0, 10), ipadx=5)

        download_button = ttk.Button(
            download_frame,
            text="Download CSV",
            command=lambda: self._handle_csv_download(filename_entry)
        )
        download_button.pack(side='bottom', padx=(0, 10), pady=30)

    def _handle_csv_download(self, filename_entry):
        """
        Validate and trigger CSV download with custom filename.
        """
        filename = filename_entry.get().strip()

        if not filename:
            messagebox.showwarning("Missing Filename", "Please enter a filename.")
            return

        # Ensure the filename ends with .csv
        if not filename.lower().endswith(".csv"):
            filename += ".csv"

        all_products = self.product_repository.get_all_products()
        successful, message = save_products_to_csv(all_products, filename)

        if not successful:
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Success", f"Products saved to {filename}")

    def show_price_graph(self, transform: bool = False, selected_products: list[str] = None):
        """Show a graph of product prices over time, with optional product filtering."""
        self.destroy_non_main_components()

        all_products = self.product_repository.get_all_products()

        # Filter products if selection is given
        if selected_products:
            all_products = [p for p in all_products if p.product_name in selected_products]

        data = {
            "date": [p.date for p in all_products],
            "product_name": [p.product_name for p in all_products],
            "price": [math.log10(p.price + 1) if transform else p.price for p in all_products],
        }

        df = pd.DataFrame(data)
        pivot = df.pivot(index='date', columns='product_name', values='price')

        # Layout
        plot_frame = ttk.Frame(self)
        plot_frame.pack(fill='both', pady=10, expand=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        pivot.plot(ax=ax, title="Product Price History", marker='o')
        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.grid(True)
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Button to open filter popup
        filter_button = ttk.Button(
            plot_frame,
            text="Filter Products",
            command=lambda: self.open_filter_popup(transform, selected_products)
        )
        filter_button.pack(side="left", padx=20, pady=10)
        ToolTip(filter_button, msg="Filter products on graph", x_offset=25, y_offset=25)

        # Transform toggle button
        text = "Normal Transform" if transform else "Log Transform"
        log_transform_button = ttk.Button(
            plot_frame,
            text=text,
            command=lambda: self.show_price_graph(not transform, selected_products)
        )
        log_transform_button.pack(side="left", padx=30, pady=10)
        message = f"Transform data {'back to Normal pricing' if transform else 'to Log10()'}"
        ToolTip(log_transform_button, msg=message, x_offset=25, y_offset=25)

    def open_filter_popup(self, transform: bool, selected_products: list[str]):
        """
        Open a resizable popup window allowing the user to select which products to display on the graph.
        :param transform: Indicates whether the current graph uses log transformation.
        :param selected_products: A list of product names currently selected (to preselect in the popup).
        """
        popup = tk.Toplevel(self)
        popup.title("Select Products")
        popup.geometry("800x600")
        popup.resizable(True, True)
        popup.columnconfigure(0, weight=1)
        popup.columnconfigure(1, weight=0)
        popup.rowconfigure(1, weight=1)

        label = ttk.Label(popup, text="Choose products to display:")
        label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 0))

        listbox = tk.Listbox(
            popup, selectmode='multiple', exportselection=False
        )
        listbox.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=10)

        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=listbox.yview)
        scrollbar.grid(row=1, column=1, sticky='ns', pady=10, padx=(0, 10))
        listbox.config(yscrollcommand=scrollbar.set)

        # Populate listbox
        all_product_names = sorted(set(p.product_name for p in self.product_repository.get_all_products()))
        for name in all_product_names:
            listbox.insert(tk.END, name)

        if selected_products:
            for i, name in enumerate(all_product_names):
                if name in selected_products:
                    listbox.select_set(i)

        # Apply button
        apply_button = ttk.Button(
            popup,
            text="Apply Filter",
            command=lambda: self._apply_filter_and_close(
                popup, listbox, all_product_names, transform
            )
        )
        apply_button.grid(row=2, column=0, columnspan=2, pady=(0, 10))

        popup.grab_set()  # Modal behavior

    def _apply_filter_and_close(self, popup, listbox, all_product_names, transform):
        """
        Apply the selected product filters from the popup and refresh the graph.
        :param popup: The popup window containing the product filter UI.
        :param listbox: The listbox widget with selectable product names.
        :param all_product_names: The complete list of product names in display order.
        :param transform: Whether to use logarithmic transformation for the prices.
        """
        selected = [all_product_names[i] for i in listbox.curselection()]
        popup.destroy()
        self.show_price_graph(transform=transform, selected_products=selected)

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

    def add_new_entry_to_products(self):
        """Open a new window to add new entries to products."""
        self.destroy_non_main_components()

        add_new_entry_frame = ttk.Frame(self)
        add_new_entry_frame.pack(pady=10, fill="both", expand=True)

        add_new_entry_label = ttk.Label(add_new_entry_frame, text="Add new entries to products")
        add_new_entry_label.pack(pady=10)

        add_row_button = ttk.Button(
            add_new_entry_frame,
            text="Add Row",
            command=lambda: self.add_new_product_row_to_table(table, columns)
        )
        add_row_button.pack(pady=10)

        # Create a Treeview table
        columns: List[str] = list(Product._meta.fields.keys())
        columns.remove('id')

        style = ttk.Style()
        style.configure("Treeview", rowheight=40)
        style.configure("Treeview.Heading", anchor="center")
        table = ttk.Treeview(add_new_entry_frame, columns=columns, show="headings")
        table.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure column headings and widths
        for column in columns:
            table.heading(column, text=column)
            table.column(column, width=150, anchor="center")

        submit_table = ttk.Button(
            add_new_entry_frame,
            text="Add new entries",
            command=lambda: self.add_new_entries_to_db(table)
        )
        submit_table.pack(pady=10)

    def add_new_product_row_to_table(self, table, columns: List[str]) -> None:
        """
        Open a new window to add a new row to the product table.
        :param table: The Treeview table to add the new row to.
        :param columns: The list of column names for the table.
        """
        new_row_window = tk.Toplevel(self)
        new_row_window.title("Add New Row")
        new_row_window.geometry("400x900")
        new_row_frame = ttk.Frame(new_row_window)
        new_row_frame.pack(pady=10, padx=10, fill="both", expand=True)
        new_row_label = ttk.Label(new_row_frame, text="Enter new row data:")
        new_row_label.pack(pady=10)
        new_row_entries = {}

        # Create entry fields for each column
        for column in columns:
            entry_frame = ttk.Frame(new_row_frame)
            entry_frame.pack(fill="x", pady=5)
            label = ttk.Label(entry_frame, text=column + ":")
            label.pack(side="left", padx=(0, 5))
            entry = ttk.Entry(entry_frame)
            entry.pack(side="left", fill="x", expand=True)
            new_row_entries[column] = entry

        # Add button to add new row to table
        def submit_new_row():
            row_data = {current_column: new_entry.get() for current_column, new_entry in new_row_entries.items()}
            stockcode = row_data.get('stockcode', '').strip()
            store = row_data.get('store', '').strip()
            date = row_data.get('date', '').strip()
            price = row_data.get('price', '').strip()
            try:
                if not date or not stockcode or not store or not price:
                    raise ValueError("Date, Stockcode, Store, and Product Name are required fields.")
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
                    raise ValueError("Date must be in YYYY-MM-DD format.")
                if not price.replace('.', '', 1).isdigit():
                    raise ValueError("Price must be a valid number.")
                row_data['price'] = float(price)
                product = self.product_coordinator.get_product_by_stockcode(stockcode=stockcode, store=store)
                row_data['product_name'] = product.product_name
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            except HTTPStatusError as e:
                messagebox.showerror("Error", f"Product with stockcode '{stockcode}' not found in store '{store}'.")
                return
            table.insert("", "end", values=list(row_data.values()))
            new_row_window.destroy()

        submit_button = ttk.Button(new_row_frame, text="Submit", command=submit_new_row)
        submit_button.pack(pady=10)

    def add_new_entries_to_db(self, table):
        # error message as it is not implemented yet
        messagebox.showerror("Error", "This feature is not implemented yet. Please try again later.")

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
