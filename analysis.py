# analysis.py
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB_NAME = "store.db"

def top_clients():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("""
        SELECT c.name, COUNT(o.order_id) AS num_orders
        FROM orders o
        JOIN clients c ON o.client_id = c.client_id
        GROUP BY c.name
        ORDER BY num_orders DESC
        LIMIT 5
    """, conn)
    sns.barplot(x="num_orders", y="name", data=df, palette="Blues_d")
    plt.title("Топ 5 клиентов по числу заказов")
    plt.xlabel("Количество заказов")
    plt.ylabel("Клиент")
    plt.show()
    conn.close()

def orders_over_time():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT order_date FROM orders", conn)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df = df.groupby("order_date").size().reset_index(name="count")
    plt.plot(df["order_date"], df["count"], marker='o')
    plt.title("Динамика заказов по датам")
    plt.xlabel("Дата")
    plt.ylabel("Количество заказов")
    plt.grid(True)
    plt.show()
    conn.close()
