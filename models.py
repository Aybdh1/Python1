# models.py
from datetime import datetime

class BaseModel:
    """Базовый класс с общими методами"""
    def to_dict(self):
        return self.__dict__

class Client(BaseModel):
    def __init__(self, client_id, name, email, phone):
        self.client_id = client_id
        self.name = name
        self.email = email
        self.phone = phone

    def __str__(self):
        return f"{self.name} ({self.email})"

class Product(BaseModel):
    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} - {self.price:.2f}₽"

class Order(BaseModel):
    def __init__(self, order_id, client_id, product_id, quantity, order_date=None):
        self.order_id = order_id
        self.client_id = client_id
        self.product_id = product_id
        self.quantity = quantity
        self.order_date = order_date or datetime.now().strftime("%Y-%m-%d")

    def __str__(self):
        return f"Заказ {self.order_id} от клиента {self.client_id}"
