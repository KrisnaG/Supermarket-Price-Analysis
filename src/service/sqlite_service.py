import sqlite3
from typing import List, Dict, Any


class SQLiteService:
    """SQLite service to manage multiple databases for product data."""

    def __init__(self, db_name: str):
        """
        Initialize the SQLiteService with a specific database.
        :param db_name: Name of the database file.
        """
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self._create_tables()

    def _create_tables(self):
        """Create tables for storing product data."""
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stockcode TEXT NOT NULL,
                    store TEXT NOT NULL,
                    name TEXT,
                    price REAL,
                    UNIQUE(stockcode, store)
                )
            """)
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS product_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stockcode TEXT NOT NULL,
                    reference_code TEXT NOT NULL,
                    UNIQUE(stockcode, reference_code)
                )
            """)

    def insert_product(self, stockcode: str, store: str, name: str, price: float):
        """
        Insert or update a product in the database.
        :param stockcode: Stock code of the product.
        :param store: Store name (e.g., Woolworths, Coles).
        :param name: Product name.
        :param price: Product price.
        """
        with self.connection:
            self.connection.execute("""
                INSERT OR REPLACE INTO products (stockcode, store, name, price)
                VALUES (?, ?, ?, ?)
            """, (stockcode, store, name, price))

    def insert_reference(self, stockcode: str, reference_code: str):
        """
        Insert a reference code for a stock code.
        :param stockcode: Stock code of the product.
        :param reference_code: Shared reference code for the product.
        """
        with self.connection:
            self.connection.execute("""
                INSERT OR IGNORE INTO product_references (stockcode, reference_code)
                VALUES (?, ?)
            """, (stockcode, reference_code))

    def get_product_by_stockcode(self, stockcode: str, store: str) -> Dict[str, Any]:
        """
        Retrieve a product by stock code and store.
        :param stockcode: Stock code of the product.
        :param store: Store name.
        :returns: Product details as a dictionary.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT stockcode, store, name, price
            FROM products
            WHERE stockcode = ? AND store = ?
        """, (stockcode, store))
        row = cursor.fetchone()
        return {"stockcode": row[0], "store": row[1], "name": row[2], "price": row[3]} if row else None

    def get_reference_by_stockcode(self, stockcode: str) -> List[str]:
        """
        Retrieve all reference codes for a stock code.
        :param stockcode: Stock code of the product.
        :returns: List of reference codes.
        """
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT reference_code
            FROM product_references
            WHERE stockcode = ?
        """, (stockcode,))
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """Close the database connection."""
        self.connection.close()