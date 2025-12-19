# main.py
from db import init_db
from gui import App
import analysis

if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()

    # Пример анализа (можно вызывать отдельно)
    # analysis.top_clients()
    # analysis.orders_over_time()
