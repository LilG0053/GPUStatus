class product:
    def __init__(self, name, price, availability):
        self.name = name
        self.price = price
        self.unavailable = availability

    def __str__(self):
        return f"Product Name: {self.name}, Price: {self.price}, Availability: {self.availability}"