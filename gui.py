import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
from db_manager import DBManager
from export_manager import ExportManager


class App(tk.Tk):
    # Style constants
    BACKGROUND_COLOR = "#1E1E1E"
    FOREGROUND_COLOR = "#E0E0E0"
    ACCENT_COLOR = "#0288D1"
    ACCENT_COLOR_ACTIVE = "#03A9F4"
    CARD_COLOR = "#2C2C2C"
    PADDING = 10
    FONT_DEFAULT = ("Helvetica", 10)
    FONT_BOLD = ("Helvetica", 10, "bold")

    def __init__(self):
        super().__init__()
        self.title("ATphonOS - DB (DuckDB) export tool")
        self.geometry("600x400")
        self.configure(bg=self.BACKGROUND_COLOR)

        # window ico (png)
        self._set_icon()

        self.db_manager = DBManager()
        self.export_manager = None
        self.db_path = ""
        self.filtered_tables = []

        self.export_options = {
            "Export Structure (SQL)": self.export_sql_structure_only,
            "Export Structure & Data (SQL)": self.export_sql,
            "Export All Tables (SQL)": self.export_all_tables_sql,
            "Export Data (SQLite)": self.export_sqlite,
            "Export Data (XML)": self.export_xml,
            "Export Data (CSV)": self.export_csv,
            "Export Data (JSON)": self.export_json,
            "Export Data (Parquet)": self.export_parquet,
            "Export Data (HTML)": self.export_html,
            "Export All Tables (HTML)": self.export_all_tables_html,
        }

        self.init_ui()
        self.apply_styles()

    def _set_icon(self):
        try:
            if getattr(sys, "frozen", False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            icon_path = os.path.join(base_path, "icon", "logo_app.png")
            if os.path.exists(icon_path):
                self.icon_image = tk.PhotoImage(file=icon_path)
                self.iconphoto(True, self.icon_image)
            else:
                print(f"Icon not found in: {icon_path}")
        except Exception as e:
            print(f"Error loading icon: {str(e)}")

    def init_ui(self):
        top_frame = tk.Frame(self, bg=self.BACKGROUND_COLOR)
        top_frame.pack(fill=tk.X, padx=self.PADDING, pady=(self.PADDING, 5))

        self.db_button = ttk.Button(
            top_frame,
            text="Open DB",
            command=self.select_database,
            style="Custom.TButton",
        )
        self.db_button.pack(side=tk.LEFT, padx=5)

        self.preview_button = ttk.Button(
            top_frame, text="Preview", command=self.show_preview, style="Custom.TButton"
        )
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.export_button = ttk.Button(
            top_frame, text="Export", style="Custom.TButton"
        )
        self.export_button.pack(side=tk.LEFT, padx=5)

        search_inner_frame = tk.Frame(top_frame, bg=self.BACKGROUND_COLOR)
        search_inner_frame.pack(side=tk.RIGHT)

        tk.Label(
            search_inner_frame,
            text="Search:",
            fg=self.FOREGROUND_COLOR,
            bg=self.BACKGROUND_COLOR,
            font=self.FONT_DEFAULT,
        ).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(
            search_inner_frame,
            bg=self.CARD_COLOR,
            fg=self.FOREGROUND_COLOR,
            font=self.FONT_DEFAULT,
            width=25,
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_tables)

        self.progress = ttk.Progressbar(
            self, orient="horizontal", length=200, mode="determinate"
        )
        self.progress.pack(pady=(0, self.PADDING))

        self.export_menu = tk.Menu(
            self,
            tearoff=0,
            bg=self.BACKGROUND_COLOR,
            fg="#FFFFFF",
            font=self.FONT_DEFAULT,
        )
        for option, command in self.export_options.items():
            self.export_menu.add_command(label=option, command=command)
        self.export_button.bind(
            "<Button-1>", lambda event: self.show_export_menu(event)
        )

        self.tables_frame = tk.LabelFrame(
            self,
            text="Open DB to load the tables",
            font=self.FONT_BOLD,
            fg=self.FOREGROUND_COLOR,
            bg=self.CARD_COLOR,
            bd=1,
            relief="flat",
            padx=5,
            pady=5,
        )
        self.tables_frame.pack(fill=tk.BOTH, expand=True, padx=self.PADDING, pady=5)

        self.listbox = tk.Listbox(
            self.tables_frame,
            bg=self.CARD_COLOR,
            fg=self.FOREGROUND_COLOR,
            font=self.FONT_DEFAULT,
            bd=0,
            highlightthickness=0,
            selectbackground=self.ACCENT_COLOR,
            selectforeground="white",
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.db_label = tk.Label(
            self,
            text="DB: not selected",
            font=self.FONT_DEFAULT,
            fg=self.FOREGROUND_COLOR,
            bg=self.BACKGROUND_COLOR,
            anchor="w",
            cursor="hand2",
        )
        self.db_label.pack(fill=tk.X, padx=self.PADDING, pady=(0, self.PADDING))
        self.db_label.bind("<Button-1>", self.open_directory)
        self.db_label.config(underline=True)

        self.progress.pack_forget()

    def apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.TButton",
            font=self.FONT_DEFAULT,
            padding=(3, 1),
            background=self.BACKGROUND_COLOR,
            foreground="#FFFFFF",
            borderwidth=1,
            relief="flat",
        )
        style.map(
            "Custom.TButton",
            background=[("active", self.ACCENT_COLOR_ACTIVE)],
            foreground=[("active", "white")],
        )

    def show_export_menu(self, event):
        self.export_menu.post(event.x_root, event.y_root)

    def open_directory(self, event):
        if self.db_path and os.path.exists(self.db_path):
            directory = os.path.dirname(self.db_path)
            try:
                if os.name == "nt":
                    os.startfile(directory)
                elif os.name == "posix":
                    os.system(
                        f'open "{directory}"'
                        if os.uname().sysname == "Darwin"
                        else f'xdg-open "{directory}"'
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Could not open directory: {str(e)}")

    def update_tables(self):
        self.listbox.delete(0, tk.END)
        if self.db_manager.conn is None and self.db_path:
            self.db_manager.connect()
        tables = self.db_manager.get_tables()
        for table in tables:
            row_count = self.db_manager.get_row_count(table)
            self.listbox.insert(tk.END, f"{table} ({row_count} records)")
        self.filtered_tables = tables

    def filter_tables(self, event):
        search_text = self.search_entry.get().lower()
        self.listbox.delete(0, tk.END)
        if not search_text:
            self.update_tables()
            return
        for table in self.filtered_tables:
            if search_text in table.lower():
                row_count = self.db_manager.get_row_count(table)
                self.listbox.insert(tk.END, f"{table} ({row_count} records)")

    def get_selected_table(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Open a database and select a table")
            return None
        selected_text = self.listbox.get(selection[0])
        table_name = selected_text.split(" (")[0]
        return table_name

    def select_database(self):
        file_path = filedialog.askopenfilename(filetypes=[("DuckDB Files", "*.duckdb")])
        if file_path:
            try:
                self.db_manager.change_database(file_path)
                self.export_manager = ExportManager(file_path)
                self.update_tables()
                self.db_path = file_path
                self.db_label.config(text=f"DB: {file_path}")
                self.tables_frame.config(text="Tables")
                self.progress.pack_forget()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open database: {str(e)}")
            finally:
                if self.db_manager.conn and not self.db_manager.get_tables():
                    messagebox.showwarning(
                        "Warning", "The database is empty or contains no tables"
                    )

    def show_preview(self):
        table = self.get_selected_table()
        if not table or not self.export_manager:
            return
        preview_window = tk.Toplevel(self)
        preview_window.title(f"Preview - {table}")
        preview_window.geometry("800x400")
        preview_window.configure(bg=self.BACKGROUND_COLOR)

        try:
            if getattr(sys, "frozen", False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))

            icon_path = os.path.join(base_path, "icon", "logo_app.png")
            if os.path.exists(icon_path):
                icon_image = tk.PhotoImage(file=icon_path)
                preview_window.iconphoto(True, icon_image)
            else:
                print(f"Icon not found in: {icon_path}")
        except Exception as e:
            print(f"Error loading icon: {str(e)}")

        main_frame = tk.Frame(preview_window, bg=self.BACKGROUND_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        canvas = tk.Canvas(main_frame, bg=self.BACKGROUND_COLOR, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(
            main_frame, orient="horizontal", command=canvas.xview
        )
        scrollable_frame = tk.Frame(canvas, bg=self.BACKGROUND_COLOR)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        columns = [
            row[1]
            for row in self.export_manager.conn.execute(
                f"PRAGMA table_info({table})"
            ).fetchall()
        ]
        data = self.export_manager.conn.execute(f"SELECT * FROM {table}").fetchall()

        col_widths = {col: max(100, len(col) * 10) for col in columns}

        header_frame = tk.Frame(scrollable_frame, bg=self.BACKGROUND_COLOR)
        header_frame.pack(fill=tk.X)
        headers = []
        dividers = []
        divider_positions = []
        for col_idx, col in enumerate(columns):
            header_label = tk.Label(
                header_frame,
                text=col,
                font=self.FONT_BOLD,
                fg=self.FOREGROUND_COLOR,
                bg=self.BACKGROUND_COLOR,
                anchor="w",
                padx=5,
                pady=5,
                width=col_widths[col] // 10,
            )
            header_label.grid(row=0, column=col_idx * 2, sticky="nsew")
            headers.append(header_label)

            if col_idx < len(columns) - 1:
                divider_position = sum(
                    col_widths[columns[i]] for i in range(col_idx + 1)
                ) + (col_idx * 2)
                divider_positions.append(divider_position)

            if col_idx < len(columns) - 1:
                divider = tk.Frame(
                    header_frame,
                    bg=self.FOREGROUND_COLOR,
                    width=2,
                    cursor="sb_h_double_arrow",
                )
                divider.grid(row=0, column=col_idx * 2 + 1, sticky="ns")
                dividers.append(divider)

        def resize_column(event, divider_idx):
            x = event.widget.winfo_rootx() - header_frame.winfo_rootx() + event.x
            if divider_idx == 0:
                start_x = 0
            else:
                start_x = sum(col_widths[columns[i]] for i in range(divider_idx)) + (
                    divider_idx * 2
                )
            new_width = x - start_x
            if new_width > 50:
                col_widths[columns[divider_idx]] = new_width
                headers[divider_idx].config(width=new_width // 10)
                for row_frame in scrollable_frame.winfo_children()[1:]:
                    cell = row_frame.grid_slaves(row=0, column=divider_idx * 2)[0]
                    cell.config(width=new_width // 10, wraplength=new_width)
                for i in range(divider_idx + 1, len(dividers)):
                    divider_positions[i] = sum(
                        col_widths[columns[j]] for j in range(i + 1)
                    ) + (i * 2)
                canvas.configure(scrollregion=canvas.bbox("all"))

        for idx, divider in enumerate(dividers):
            divider.bind("<B1-Motion>", lambda e, i=idx: resize_column(e, i))

        def format_value(value):
            if value is None:
                return "NULL"
            return str(value)

        for row_idx, row in enumerate(data, start=1):
            row_frame = tk.Frame(scrollable_frame, bg=self.CARD_COLOR)
            row_frame.pack(fill=tk.X, pady=1)
            formatted_row = [format_value(value) for value in row]
            for col_idx, (value, col) in enumerate(zip(formatted_row, columns)):
                value_width = max(
                    100, sum(len(line) for line in str(value).split("\n")) * 7
                )
                col_widths[col] = max(col_widths[col], value_width)

                cell_label = tk.Label(
                    row_frame,
                    text=value,
                    font=self.FONT_DEFAULT,
                    fg=self.FOREGROUND_COLOR,
                    bg=self.CARD_COLOR,
                    anchor="w",
                    padx=5,
                    pady=5,
                    justify="left",
                    wraplength=col_widths[col],
                    width=col_widths[col] // 10,
                )
                cell_label.grid(row=0, column=col_idx * 2, sticky="nsew")

        for col_idx, col in enumerate(columns):
            header_frame.grid_columnconfigure(col_idx * 2, minsize=col_widths[col])
            for row_frame in scrollable_frame.winfo_children()[1:]:
                row_frame.grid_columnconfigure(col_idx * 2, minsize=col_widths[col])
            if col_idx < len(columns) - 1:
                header_frame.grid_columnconfigure(col_idx * 2 + 1, minsize=2)
                for row_frame in scrollable_frame.winfo_children()[1:]:
                    row_frame.grid_columnconfigure(col_idx * 2 + 1, minsize=2)

        ttk.Button(
            preview_window,
            text="Close",
            command=preview_window.destroy,
            style="Custom.TButton",
        ).pack(pady=5)

    def start_progress(self, max_value):
        self.progress["maximum"] = max_value
        self.progress["value"] = 0
        self.progress.pack(pady=(0, self.PADDING))

    def update_progress(self, value):
        self.progress["value"] = value
        self.update_idletasks()

    def stop_progress(self):
        self.progress.pack_forget()

    def export_sql_structure_only(self):
        table = self.get_selected_table()
        if table and self.export_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".sql", filetypes=[("SQL Files", "*.sql")]
            )
            if file_path:
                try:
                    self.start_progress(1)
                    if self.export_manager.export_table_structure_only(
                        table, file_path
                    ):
                        self.update_progress(1)
                        messagebox.showinfo(
                            "Success", f"SQL structure exported to: {file_path}"
                        )
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to export SQL structure: {str(e)}"
                    )
                finally:
                    self.stop_progress()

    def export_sql(self):
        table = self.get_selected_table()
        if table and self.export_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".sql", filetypes=[("SQL Files", "*.sql")]
            )
            if file_path:
                try:
                    row_count = self.db_manager.get_row_count(table)
                    self.start_progress(row_count)
                    if self.export_manager.export_table_sql(table, file_path):
                        self.update_progress(row_count)
                        messagebox.showinfo(
                            "Success",
                            f"SQL structure and data exported to: {file_path}",
                        )
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export to SQL: {str(e)}")
                finally:
                    self.stop_progress()

    def export_csv(self):
        table = self.get_selected_table()
        if table and self.export_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
            )
            if file_path:
                try:
                    row_count = self.db_manager.get_row_count(table)
                    self.start_progress(row_count)
                    if self.export_manager.export_table_csv(table, file_path):
                        self.update_progress(row_count)
                        messagebox.showinfo(
                            "Success", f"Data exported to CSV: {file_path}"
                        )
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export to CSV: {str(e)}")
                finally:
                    self.stop_progress()

    def export_json(self):
        table = self.get_selected_table()
        if table and self.export_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json", filetypes=[("JSON Files", "*.json")]
            )
            if file_path:
                try:
                    row_count = self.db_manager.get_row_count(table)
                    self.start_progress(row_count)
                    if self.export_manager.export_table_json(table, file_path):
                        self.update_progress(row_count)
                        messagebox.showinfo(
                            "Success", f"Data exported to JSON: {file_path}"
                        )
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to export to JSON: {str(e)}")
                finally:
                    self.stop_progress()

    def export_parquet(self):
        table = self.get_selected_table()
        if table and self.export_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".parquet", filetypes=[("Parquet Files", "*.parquet")]
            )
            if file_path:
                try:
                    row_count = self.db_manager.get_row_count(table)
                    self.start_progress(row_count)
                    if self.export_manager.export_table_parquet(table, file_path):
                        self.update_progress(row_count)
                        messagebox.showinfo(
                            "Success", f"Data exported to Parquet: {file_path}"
                        )
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to export to Parquet: {str(e)}"
                    )
                finally:
                    self.stop_progress()

    def export_html(self):
        table = self.get_selected_table()
        if table and self.export_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html", filetypes=[("HTML Files", "*.html")]
            )
            if file_path:
                try:
                    row_count = self.db_manager.get_row_count(table)
                    self.start_progress(row_count)
                    if self.export_manager.export_table_html(table, file_path):
                        self.update_progress(row_count)
                        messagebox.showinfo(
                            "Success", f"Data exported to HTML: {file_path}"
                        )
                except Exception as e:
                    messagebox.showerror("Error", f"Could not export to HTML: {str(e)}")
                finally:
                    self.stop_progress()

    def export_all_tables_sql(self):
        if not self.db_manager.get_tables():
            messagebox.showwarning("Warning", "There are no tables to export")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sql", filetypes=[("SQL Files", "*.sql")]
        )
        if file_path:
            try:
                tables = self.db_manager.get_tables()
                self.start_progress(len(tables))
                with open(file_path, "w", encoding="utf-8") as f:
                    for i, table in enumerate(tables, 1):
                        schema = self.export_manager.get_create_table_sql(table)
                        f.write(schema + "\n\n")
                        data = self.export_manager.conn.execute(
                            f"SELECT * FROM {table}"
                        ).fetchall()
                        columns = [
                            row[1]
                            for row in self.export_manager.conn.execute(
                                f"PRAGMA table_info({table})"
                            ).fetchall()
                        ]
                        for row in data:
                            values = ", ".join(
                                self.export_manager._escape_value(v) for v in row
                            )
                            f.write(
                                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({values});\n"
                            )
                        self.update_progress(i)
                self.stop_progress()
                messagebox.showinfo("Success", f"All tables exported to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export all tables: {str(e)}")
                self.stop_progress()

    def export_all_tables_html(self):
        if not self.db_manager.get_tables():
            messagebox.showwarning("Warning", "There are no tables to export")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html", filetypes=[("HTML Files", "*.html")]
        )
        if file_path:
            try:
                tables = self.db_manager.get_tables()
                self.start_progress(len(tables))
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("<!DOCTYPE html>\n<html>\n<head>\n")
                    f.write("<title>All Tables Export</title>\n")
                    f.write("<style>\n")
                    f.write(
                        "table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }\n"
                    )
                    f.write(
                        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; white-space: pre-wrap; }\n"
                    )
                    f.write("th { background-color: #f2f2f2; }\n")
                    f.write("tr:nth-child(even) { background-color: #f9f9f9; }\n")
                    f.write("</style>\n")
                    f.write("</head>\n<body>\n")
                    for i, table in enumerate(tables, 1):
                        f.write(f"<h2>Table: {table}</h2>\n")
                        f.write("<table>\n")
                        data = self.export_manager.conn.execute(
                            f"SELECT * FROM {table}"
                        ).fetchall()
                        columns = [
                            row[1]
                            for row in self.export_manager.conn.execute(
                                f"PRAGMA table_info({table})"
                            ).fetchall()
                        ]
                        f.write("<tr>\n")
                        for col in columns:
                            f.write(
                                f"<th>{self.export_manager._escape_html(col)}</th>\n"
                            )
                        f.write("</tr>\n")
                        for row in data:
                            f.write("<tr>\n")
                            for value in row:
                                f.write(
                                    f"<td>{self.export_manager._escape_html(value)}</td>\n"
                                )
                            f.write("</tr>\n")
                        f.write("</table>\n")
                        self.update_progress(i)
                    f.write("</body>\n</html>")
                self.stop_progress()
                messagebox.showinfo("Success", f"All tables exported to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export all tables: {str(e)}")
                self.stop_progress()

    def export_sqlite(self):
        table = self.get_selected_table()
        if table and self.export_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".db", filetypes=[("SQLite Files", "*.db")]
            )
            if file_path:
                try:
                    row_count = self.db_manager.get_row_count(table)
                    self.start_progress(row_count)
                    if self.export_manager.export_table_sqlite(table, file_path):
                        self.update_progress(row_count)
                        messagebox.showinfo(
                            "Success", f"Data exported to SQLite: {file_path}"
                        )
                except Exception as e:
                    messagebox.showerror(
                        "Error", f"Failed to export to SQLite: {str(e)}"
                    )
                finally:
                    self.stop_progress()

    def export_xml(self):
        table = self.get_selected_table()
        if table and self.export_manager:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xml", filetypes=[("XML Files", "*.xml")]
            )
            if file_path:
                try:
                    row_count = self.db_manager.get_row_count(table)
                    self.start_progress(row_count)
                    if self.export_manager.export_table_xml(table, file_path):
                        self.update_progress(row_count)
                        messagebox.showinfo(
                            "Success", f"Data exported to XML: {file_path}"
                        )
                except Exception as e:
                    messagebox.showerror("Error", f"Could not export to XML: {str(e)}")
                finally:
                    self.stop_progress()

    def __del__(self):
        if self.db_manager:
            self.db_manager.close()
        if self.export_manager:
            self.export_manager.close()

