from datetime import datetime

class Item:
    def __init__(self, name, cost_price, sell_price, quantity, representative):
        self.name = name
        self.cost_price = cost_price
        self.sell_price = sell_price
        self.quantity = quantity
        self.representative = representative

    def total_cost(self):
        return self.cost_price * self.quantity

    def total_price(self):
        return self.sell_price * self.quantity

    def profit(self):
        return self.total_price() - self.total_cost()

import uuid
from datetime import datetime

class Order:
    def __init__(self, client, items, amount_paid, issue_date=None, submission_date=None, status="in_progress", notes=""):
        self.order_id = self.generate_id()
        self.client = client
        self.items = items
        self.amount_paid = amount_paid
        self.issue_date = issue_date if issue_date else datetime.today().strftime("%Y-%m-%d")
        self.submission_date = submission_date
        self.status = status
        self.notes = notes

    def generate_id(self):
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        short_uid = str(uuid.uuid4())[:6].upper()
        return f"{date_str}-{short_uid}"

    def total_price(self):
        return sum(item.total_price() for item in self.items)

    def total_cost(self):
        return sum(item.total_cost() for item in self.items)

    def profit(self):
        return self.total_price() - self.total_cost()

    def remaining_balance(self):
        return self.total_price() - self.amount_paid
