import duckdb
import os


class DBManager:

    def __init__(self):
        self.db_path = None
        self.conn = None

    def connect(self):
        if not self.db_path or not os.path.exists(self.db_path):
            raise ValueError("Invalid or unselected database path")
        self.conn = duckdb.connect(self.db_path)

    def change_database(self, new_db_path):
        self.db_path = new_db_path
        if self.conn:
            self.conn.close()
        self.connect()

    def get_tables(self):
        if not self.conn:
            self.connect()
        return [row[0] for row in self.conn.execute("SHOW TABLES").fetchall()]

    def get_row_count(self, table_name):
        if not self.conn:
            self.connect()
        result = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        return result[0] if result else 0

    def get_table_schema(self, table_name):
        if not self.conn:
            self.connect()
        result = self.conn.execute(f"SHOW CREATE TABLE {table_name}").fetchall()
        return result[0][0] if result else ""

    def export_database_sql(self, export_path):
        if not self.conn:
            self.connect()
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        self.conn.execute(f"EXPORT DATABASE '{export_path}' (FORMAT SQL)")

    def copy_database(self, new_path):
        if not self.conn:
            self.connect()
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        self.conn.execute(f"EXPORT DATABASE '{new_path}' (FORMAT PARQUET)")

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.db_path = None

    def __del__(self):
        self.close()
