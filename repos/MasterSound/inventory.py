import csv

# Sample product data: code, description, price, quantity
products = [
    {"code": "P001", "description": "Headphones", "price": 59.99, "quantity": 25},
    {"code": "P002", "description": "Microphone", "price": 89.50, "quantity": 15},
    {"code": "P003", "description": "Audio Interface", "price": 129.00, "quantity": 10},
    {"code": "P004", "description": "Mixer", "price": 199.99, "quantity": 5},
    {"code": "P005", "description": "Studio Monitor", "price": 149.75, "quantity": 8},
]

# Define CSV file path
csv_file = "inventory.csv"

# Write to CSV
with open(csv_file, mode="w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["code", "description", "price", "quantity"])
    writer.writeheader()
    for product in products:
        writer.writerow(product)

print(f"Inventory CSV generated at {csv_file}")
