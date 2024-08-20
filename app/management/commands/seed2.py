from django.core.management.base import BaseCommand
from app.models import Product, Category, ProductDetail
from cloudinary.models import CloudinaryField


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.seed_custom_users()
        self.seed_categories()
        self.seed_products()
        self.seed_species()
        self.seed_product_details()
        self.seed_bills()
        self.seed_bill_details()
        self.seed_comments()
        self.seed_vouchers()
        self.seed_voucher_histories()
        self.seed_carts()
        self.seed_cart_details()
        self.stdout.write(self.style.SUCCESS(
            'Successfully seeded the database'))

    def seed_custom_users(self):
        # Example implementation (not updated)
        pass

    def seed_categories(self):
        # Example implementation (not updated)
        pass

    def seed_products(self):
        categories = Category.objects.all()
        products = [{'name': 'Laptop',
                     'category': categories[0],
                     'price': 1000,
                     'description': 'A high performance laptop',
                     'sold_quantity': 15},
                    {'name': 'Smartphone',
                     'category': categories[0],
                     'price': 600,
                     'description': 'A latest model smartphone',
                     'sold_quantity': 30},
                    {'name': 'Headphones',
                     'category': categories[0],
                     'price': 150,
                     'description': 'Noise-cancelling headphones',
                     'sold_quantity': 50},
                    {'name': 'Smartwatch',
                     'category': categories[0],
                     'price': 200,
                     'description': 'A smartwatch with various features',
                     'sold_quantity': 20},
                    {'name': 'Bluetooth Speaker',
                     'category': categories[0],
                     'price': 80,
                     'description': 'Portable Bluetooth speaker',
                     'sold_quantity': 45},
                    {'name': 'Fiction Book',
                     'category': categories[1],
                     'price': 20,
                     'description': 'An engaging fiction novel',
                     'sold_quantity': 100},
                    {'name': 'Non-Fiction Book',
                     'category': categories[1],
                     'price': 25,
                     'description': 'A comprehensive non-fiction book',
                     'sold_quantity': 80},
                    {'name': 'Cookbook',
                     'category': categories[1],
                     'price': 30,
                     'description': 'Delicious recipes for home cooking',
                     'sold_quantity': 60},
                    {'name': 'T-Shirt',
                     'category': categories[2],
                     'price': 15,
                     'description': 'A comfortable cotton T-shirt',
                     'sold_quantity': 120},
                    {'name': 'Jeans',
                     'category': categories[2],
                     'price': 40,
                     'description': 'Stylish and durable jeans',
                     'sold_quantity': 90}]
        for product in products:
            Product.objects.create(
                name=product['name'],
                category=product['category'],
                price=product['price'],
                description=product['description'],
                average_rating=4.0,  # Set a default average rating
                sold_quantity=product['sold_quantity']
            )

    def seed_species(self):
        # Example implementation (not updated)
        pass

    def seed_product_details(self):
        # Example implementation (not updated)
        pass

    def seed_bills(self):
        # Example implementation (not updated)
        pass

    def seed_bill_details(self):
        # Example implementation (not updated)
        pass

    def seed_comments(self):
        # Example implementation (not updated)
        pass

    def seed_vouchers(self):
        # Example implementation (not updated)
        pass

    def seed_voucher_histories(self):
        # Example implementation (not updated)
        pass

    def seed_carts(self):
        # Example implementation (not updated)
        pass

    def seed_cart_details(self):
        # Example implementation (not updated)
        pass
