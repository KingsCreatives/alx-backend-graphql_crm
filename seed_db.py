import os
import django
from decimal import Decimal
from django.utils import timezone
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order  

def seed_customers():
    """Seed initial customers."""
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+233201234567"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Danvers", "email": "carol@example.com", "phone": "+233541234567"},
        {"name": "David Miller", "email": "david@example.com"},
    ]

    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(email=data["email"], defaults=data)
        if created:
            print(f"✅ Created customer: {customer.name}")
        else:
            print(f"⚠️ Customer already exists: {customer.name}")
        customers.append(customer)
    return customers


def seed_products():
    """Seed initial products."""
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Smartphone", "price": Decimal("699.99"), "stock": 25},
        {"name": "Tablet", "price": Decimal("399.99"), "stock": 15},
        {"name": "Wireless Headphones", "price": Decimal("199.99"), "stock": 30},
        {"name": "Smartwatch", "price": Decimal("249.99"), "stock": 20},
    ]

    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(name=data["name"], defaults=data)
        if created:
            print(f"✅ Created product: {product.name}")
        else:
            print(f"⚠️ Product already exists: {product.name}")
        products.append(product)
    return products


def seed_orders(customers, products):
    """Seed a few sample orders linking customers and products."""
    if not customers or not products:
        print("⚠️ Cannot create orders — customers or products missing.")
        return

    for i in range(3):  # create 3 sample orders
        customer = random.choice(customers)
        selected_products = random.sample(products, k=random.randint(1, 3))
        total_amount = sum(p.price for p in selected_products)

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=timezone.now(),
        )
        order.products.set(selected_products)
        print(f"✅ Created order #{order.id} for {customer.name} with {len(selected_products)} products.")


def run():
    print("\n🚀 Starting database seeding...\n")
    customers = seed_customers()
    products = seed_products()
    seed_orders(customers, products)
    print("\n🎉 Database seeding completed successfully!\n")


if __name__ == "__main__":
    run()
