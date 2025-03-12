import duckdb
import sqlite3


class ExportManager:

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)

    def _escape_value(self, value):
        if value is None:
            return "NULL"
        if isinstance(value, str):
            escaped_value = value.replace("'", "''")
            return "'" + escaped_value + "'"
        return str(value)

    def _escape_html(self, value):
        if value is None:
            return "NULL"
        value = str(value)
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def get_create_table_sql(self, table_name):
        result = self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        if not result:
            raise ValueError(f"Table '{table_name}' does not exist in the database")
        columns = []
        for row in result:
            col_name, col_type, not_null, default = row[1], row[2], bool(row[3]), row[4]
            not_null_clause = "NOT NULL" if not_null else ""
            default_clause = (
                f"DEFAULT {self._escape_value(default)}" if default is not None else ""
            )
            col_definition = (
                f"{col_name} {col_type} {not_null_clause} {default_clause}".strip()
            )
            columns.append(col_definition)

        return "CREATE TABLE {} (\n    {}\n);".format(
            table_name, ",\n    ".join(columns)
        )

    def export_table_structure_only(self, table_name, output_file):
        schema = self.get_create_table_sql(table_name)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(schema + "\n")
        return True

    def export_table_sql(self, table_name, output_file):
        schema = self.get_create_table_sql(table_name)
        data = self.conn.execute(f"SELECT * FROM {table_name}").fetchall()
        columns = [
            row[1]
            for row in self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(schema + "\n\n")
            for row in data:
                values = ", ".join(self._escape_value(v) for v in row)
                f.write(
                    f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({values});\n"
                )
        return True

    def export_table_csv(self, table_name, output_file):
        self.conn.execute(f"COPY {table_name} TO '{output_file}' (FORMAT CSV, HEADER)")
        return True

    def export_table_json(self, table_name, output_file):
        self.conn.execute(f"COPY {table_name} TO '{output_file}' (FORMAT JSON)")
        return True

    def export_table_parquet(self, table_name, output_file):
        self.conn.execute(f"COPY {table_name} TO '{output_file}' (FORMAT PARQUET)")
        return True

    def export_table_html(self, table_name, output_file):
        data = self.conn.execute(f"SELECT * FROM {table_name}").fetchall()
        columns = [
            row[1]
            for row in self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html>\n<html>\n<head>\n")
            f.write("<title>Table Export</title>\n")
            f.write("<style>\n")
            f.write("table { border-collapse: collapse; width: 100%; }\n")
            f.write(
                "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }\n"
            )
            f.write("th { background-color: #f2f2f2; }\n")
            f.write("tr:nth-child(even) { background-color: #f9f9f9; }\n")
            f.write("</style>\n")
            f.write("</head>\n<body>\n")
            f.write(f"<h2>Table: {table_name}</h2>\n")
            f.write("<table>\n")

            # Headers
            f.write("<tr>\n")
            for col in columns:
                f.write(f"<th>{self._escape_html(col)}</th>\n")
            f.write("</tr>\n")

            # Data rows
            for row in data:
                f.write("<tr>\n")
                for value in row:
                    f.write(f"<td>{self._escape_html(value)}</td>\n")
                f.write("</tr>\n")

            f.write("</table>\n")
            f.write("</body>\n</html>")
        return True

    def export_table_sqlite(self, table_name, output_file):

        sqlite_conn = sqlite3.connect(output_file)
        sqlite_cursor = sqlite_conn.cursor()

        schema = self.get_create_table_sql(table_name)

        schema = schema.rstrip(";")

        try:

            sqlite_cursor.execute(schema)

            data = self.conn.execute(f"SELECT * FROM {table_name}").fetchall()
            columns = [
                row[1]
                for row in self.conn.execute(
                    f"PRAGMA table_info({table_name})"
                ).fetchall()
            ]

            if data:
                placeholders = ", ".join(["?" for _ in columns])
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                sqlite_cursor.executemany(insert_sql, data)

            sqlite_conn.commit()
            return True
        except Exception as e:
            print(f"Error exporting to SQLite: {str(e)}")
            return False
        finally:
            sqlite_conn.close()

    def export_table_xml(self, table_name, output_file):
        columns = [
            row[1]
            for row in self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]
        data = self.conn.execute(f"SELECT * FROM {table_name}").fetchall()

        with open(output_file, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(f'<table name="{table_name}">\n')
            f.write("  <columns>\n")
            for col in columns:
                f.write(f"    <column>{self._escape_html(col)}</column>\n")
            f.write("  </columns>\n")
            f.write("  <rows>\n")
            for row in data:
                f.write("    <row>\n")
                for i, value in enumerate(row):
                    f.write(
                        f"      <{columns[i]}>{self._escape_html(value)}</{columns[i]}>\n"
                    )
                f.write("    </row>\n")
            f.write("  </rows>\n")
            f.write("</table>\n")
        return True

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __del__(self):
        self.close()
