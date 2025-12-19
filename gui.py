# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from db import add_client, add_product, add_order, get_table, export_to_csv, export_to_json, DB_NAME
import sqlite3
import csv
import json

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система учёта заказов")
        self.geometry("900x600")

        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True)

        self.client_tab = ttk.Frame(notebook)
        self.product_tab = ttk.Frame(notebook)
        self.order_tab = ttk.Frame(notebook)
        self.data_tab = ttk.Frame(notebook)

        notebook.add(self.client_tab, text="Клиенты")
        notebook.add(self.product_tab, text="Товары")
        notebook.add(self.order_tab, text="Заказы")
        notebook.add(self.data_tab, text="Импорт / Экспорт")

        self.create_client_tab()
        self.create_product_tab()
        self.create_order_tab()
        self.create_data_tab()

    # ----------------------- КЛИЕНТЫ -----------------------
    def create_client_tab(self):
        tk.Label(self.client_tab, text="Имя клиента").pack()
        name = tk.Entry(self.client_tab); name.pack()
        tk.Label(self.client_tab, text="Email").pack()
        email = tk.Entry(self.client_tab); email.pack()
        tk.Label(self.client_tab, text="Телефон").pack()
        phone = tk.Entry(self.client_tab); phone.pack()

        tk.Button(self.client_tab, text="Добавить клиента",
                  command=lambda: self.add_client_action(name, email, phone)).pack(pady=5)

        tk.Button(self.client_tab, text="Показать клиентов",
                  command=self.show_clients).pack(pady=5)

        self.client_tree = ttk.Treeview(self.client_tab, columns=("ID", "Имя", "Email", "Телефон"), show="headings")
        for col in ("ID", "Имя", "Email", "Телефон"):
            self.client_tree.heading(col, text=col)
        self.client_tree.pack(fill="both", expand=True)

    def add_client_action(self, name, email, phone):
        add_client(name.get(), email.get(), phone.get())
        messagebox.showinfo("Успех", "Клиент добавлен!")
        name.delete(0, tk.END); email.delete(0, tk.END); phone.delete(0, tk.END)
        self.show_clients()

    def show_clients(self):
        for i in self.client_tree.get_children():
            self.client_tree.delete(i)
        for row in get_table("clients"):
            self.client_tree.insert("", "end", values=row)

    # ----------------------- ТОВАРЫ -----------------------
    def create_product_tab(self):
        tk.Label(self.product_tab, text="Название товара").pack()
        name = tk.Entry(self.product_tab); name.pack()
        tk.Label(self.product_tab, text="Цена").pack()
        price = tk.Entry(self.product_tab); price.pack()

        tk.Button(self.product_tab, text="Добавить товар",
                  command=lambda: self.add_product_action(name, price)).pack(pady=5)

        tk.Button(self.product_tab, text="Показать товары",
                  command=self.show_products).pack(pady=5)

        self.product_tree = ttk.Treeview(self.product_tab, columns=("ID", "Название", "Цена"), show="headings")
        for col in ("ID", "Название", "Цена"):
            self.product_tree.heading(col, text=col)
        self.product_tree.pack(fill="both", expand=True)

    def add_product_action(self, name, price):
        try:
            add_product(name.get(), float(price.get()))
            messagebox.showinfo("Успех", "Товар добавлен!")
            name.delete(0, tk.END); price.delete(0, tk.END)
            self.show_products()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную цену!")

    def show_products(self):
        for i in self.product_tree.get_children():
            self.product_tree.delete(i)
        for row in get_table("products"):
            self.product_tree.insert("", "end", values=row)

    # ----------------------- ЗАКАЗЫ -----------------------
    def create_order_tab(self):
        from tkinter.ttk import Combobox

        tk.Label(self.order_tab, text="Клиент").pack()
        self.client_combo = Combobox(self.order_tab, state="readonly")
        self.client_combo.pack()

        tk.Label(self.order_tab, text="Товар").pack()
        self.product_combo = Combobox(self.order_tab, state="readonly")
        self.product_combo.pack()

        tk.Label(self.order_tab, text="Количество").pack()
        self.quantity_entry = tk.Entry(self.order_tab)
        self.quantity_entry.pack()

        tk.Button(self.order_tab, text="Создать заказ",
                  command=self.create_order_action).pack(pady=5)

        tk.Button(self.order_tab, text="Показать заказы",
                  command=self.show_orders).pack(pady=5)

        self.order_tree = ttk.Treeview(self.order_tab,
                                       columns=("ID", "Клиент", "Товар", "Количество", "Дата"),
                                       show="headings")
        for col in ("ID", "Клиент", "Товар", "Количество", "Дата"):
            self.order_tree.heading(col, text=col)
        self.order_tree.pack(fill="both", expand=True)

        self.refresh_order_combos()

    def refresh_order_combos(self):
        clients = get_table("clients")
        client_names = [f"{c[0]} — {c[1]}" for c in clients]
        self.client_combo["values"] = client_names

        products = get_table("products")
        product_names = [f"{p[0]} — {p[1]} ({p[2]}₽)" for p in products]
        self.product_combo["values"] = product_names

    def create_order_action(self):
        try:
            client_id = int(self.client_combo.get().split(" — ")[0])
            product_id = int(self.product_combo.get().split(" — ")[0])
            quantity = int(self.quantity_entry.get())
            add_order(client_id, product_id, quantity, datetime.now().strftime("%Y-%m-%d"))
            messagebox.showinfo("Успех", "Заказ создан!")
            self.quantity_entry.delete(0, tk.END)
            self.show_orders()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_orders(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            SELECT o.order_id, c.name, p.name, o.quantity, o.order_date
            FROM orders o
            JOIN clients c ON o.client_id = c.client_id
            JOIN products p ON o.product_id = p.product_id
        """)
        rows = cur.fetchall()
        conn.close()

        for i in self.order_tree.get_children():
            self.order_tree.delete(i)
        for row in rows:
            self.order_tree.insert("", "end", values=row)

        self.refresh_order_combos()

    # ----------------------- ИМПОРТ / ЭКСПОРТ -----------------------
    def create_data_tab(self):
        tk.Label(self.data_tab, text="Экспорт / Импорт данных", font=("Arial", 12, "bold")).pack(pady=10)

        # Экспорт
        tk.Label(self.data_tab, text="Экспорт таблицы в CSV/JSON").pack()
        self.export_table_combo = ttk.Combobox(self.data_tab, values=["clients", "products", "orders"], state="readonly")
        self.export_table_combo.pack()

        tk.Button(self.data_tab, text="Экспорт в CSV", command=self.export_csv_action).pack(pady=5)
        tk.Button(self.data_tab, text="Экспорт в JSON", command=self.export_json_action).pack(pady=5)

        # Импорт
        tk.Label(self.data_tab, text="Импорт CSV/JSON в таблицу").pack(pady=10)
        self.import_table_combo = ttk.Combobox(self.data_tab, values=["clients", "products", "orders"], state="readonly")
        self.import_table_combo.pack()

        tk.Button(self.data_tab, text="Импорт из CSV", command=self.import_csv_action).pack(pady=5)
        tk.Button(self.data_tab, text="Импорт из JSON", command=self.import_json_action).pack(pady=5)

    def export_csv_action(self):
        table = self.export_table_combo.get()
        if not table:
            messagebox.showwarning("Ошибка", "Выберите таблицу!")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if filename:
            export_to_csv(table, filename)
            messagebox.showinfo("Успех", f"Данные таблицы '{table}' экспортированы в {filename}")

    def export_json_action(self):
        table = self.export_table_combo.get()
        if not table:
            messagebox.showwarning("Ошибка", "Выберите таблицу!")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if filename:
            export_to_json(table, filename)
            messagebox.showinfo("Успех", f"Данные таблицы '{table}' экспортированы в {filename}")

    def import_csv_action(self):
        table = self.import_table_combo.get()
        if not table:
            messagebox.showwarning("Ошибка", "Выберите таблицу!")
            return
        file = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not file:
            return
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        with open(file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                placeholders = ','.join(['?'] * len(row))
                cur.execute(f"INSERT INTO {table} VALUES (NULL,{placeholders[2:]})" if table != "orders" else
                            f"INSERT INTO {table} VALUES (NULL,?,?,?,?)", row)
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", f"Данные импортированы в {table}")

    def import_json_action(self):
        table = self.import_table_combo.get()
        if not table:
            messagebox.showwarning("Ошибка", "Выберите таблицу!")
            return
        file = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not file:
            return
        with open(file, encoding='utf-8') as f:
            data = json.load(f)
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        for row in data:
            placeholders = ','.join(['?'] * len(row))
            cur.execute(f"INSERT INTO {table} VALUES (NULL,{placeholders[2:]})" if table != "orders" else
                        f"INSERT INTO {table} VALUES (NULL,?,?,?,?)", row[1:])
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", f"Данные импортированы из {file} в таблицу {table}")
