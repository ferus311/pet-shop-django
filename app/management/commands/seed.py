from django.core.management.base import BaseCommand
from app.models import (
    CustomUser, Category, Product, Species, ProductDetail,
    Bill, BillDetail, Comment, Voucher, VoucherHistory, Cart, CartDetail
)
from django.utils import timezone
from datetime import timedelta
import pyotp


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
        users = [
            {'username': 'user1', 'email': 'user1@gmail.com',
                'first_name': 'First1', 'last_name': 'Last1'},
            {'username': 'user2', 'email': 'user2@gmail.com',
                'first_name': 'First2', 'last_name': 'Last2'},
            # Thêm nhiều người dùng khác ở đây
        ]
        for user in users:
            CustomUser.objects.create(
                username=user['username'],
                email=user['email'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                default_address='123 Main Street',
                default_phone_number='0123456789'
            )

    def seed_categories(self):
        categories = [
            {'name': 'Electronics'},
            {'name': 'Books'},
            {'name': 'Clothing'},
            # Thêm nhiều danh mục khác ở đây
        ]
        for category in categories:
            Category.objects.create(name=category['name'])

    def seed_products(self):
        categories = Category.objects.all()
        products = [
            {'name': 'Laptop',
             'category': categories[0],
             'price': 1000,
             'description': 'A high performance laptop'},
            {'name': 'Python Programming',
             'category': categories[1],
             'price': 50,
             'description': 'A comprehensive guide to Python'},
            # Thêm nhiều sản phẩm khác ở đây
        ]
        for product in products:
            Product.objects.create(
                name=product['name'],
                category=product['category'],
                price=product['price'],
                description=product['description'],
                average_rating=4.5
            )

    def seed_species(self):
        species = [
            {'name': 'Mammals'},
            {'name': 'Birds'},
            # Thêm nhiều loài khác ở đây
        ]
        for specie in species:
            Species.objects.create(name=specie['name'])

    def seed_product_details(self):
        products = Product.objects.all()
        details = [
            {'product': products[0],
             'size': '15 inch',
             'color': 'Black',
             'price': 1000,
             'remain_quantity': 10},
            {'product': products[1],
             'size': 'N/A',
             'color': 'Blue',
             'price': 50,
             'remain_quantity': 50},
            # Thêm nhiều chi tiết sản phẩm khác ở đây
        ]
        for detail in details:
            ProductDetail.objects.create(
                product=detail['product'],
                size=detail['size'],
                color=detail['color'],
                price=detail['price'],
                remain_quantity=detail['remain_quantity']
            )

    def seed_bills(self):
        users = CustomUser.objects.all()
        bills = [
            {'user': users[0],
             'address': '123 Main Street',
             'phone_number': '0123456789',
             'total': 1050,
             'payment_method': 'Credit Card',
             'status': 'Paid'},
            {'user': users[1],
             'address': '456 Elm Street',
             'phone_number': '0987654321',
             'total': 50,
             'payment_method': 'PayPal',
             'status': 'Pending'},
            # Thêm nhiều hóa đơn khác ở đây
        ]
        for bill in bills:
            Bill.objects.create(
                user=bill['user'],
                address=bill['address'],
                phone_number=bill['phone_number'],
                total=bill['total'],
                payment_method=bill['payment_method'],
                status=bill['status']
            )

    def seed_bill_details(self):
        bills = Bill.objects.all()
        details = [
            {'bill': bills[0],
             'product_detail': ProductDetail.objects.first(),
             'quantity': 1},
            {'bill': bills[1],
             'product_detail': ProductDetail.objects.last(),
             'quantity': 2},
            # Thêm nhiều chi tiết hóa đơn khác ở đây
        ]
        for detail in details:
            BillDetail.objects.create(
                bill=detail['bill'],
                product_detail=detail['product_detail'],
                quantity=detail['quantity']
            )

    def seed_comments(self):
        users = CustomUser.objects.all()
        products = Product.objects.all()
        comments = [
            {'user': users[0], 'product': products[0],
                'content': 'Great product!', 'star': 5},
            {'user': users[1], 'product': products[1],
                'content': 'Very informative.', 'star': 4},
            # Thêm nhiều bình luận khác ở đây
        ]
        for comment in comments:
            Comment.objects.create(
                user=comment['user'],
                product=comment['product'],
                content=comment['content'],
                star=comment['star']
            )

    def seed_vouchers(self):
        vouchers = [
            {'discount': 10,
             'started_at': timezone.now(),
             'ended_at': timezone.now() + timedelta(days=10)},
            {'discount': 20,
             'started_at': timezone.now(),
             'ended_at': timezone.now() + timedelta(days=20)},
            # Thêm nhiều voucher khác ở đây
        ]
        for voucher in vouchers:
            Voucher.objects.create(
                discount=voucher['discount'],
                started_at=voucher['started_at'],
                ended_at=voucher['ended_at'],
                is_global=True
            )

    def seed_voucher_histories(self):
        users = CustomUser.objects.all()
        vouchers = Voucher.objects.all()
        histories = [
            {'user': users[0], 'voucher': vouchers[0]},
            {'user': users[1], 'voucher': vouchers[1]},
            # Thêm nhiều lịch sử voucher khác ở đây
        ]
        for history in histories:
            VoucherHistory.objects.create(
                user=history['user'],
                voucher=history['voucher']
            )

    def seed_carts(self):
        users = CustomUser.objects.all()
        carts = [
            {'user': users[0], 'total': 1000},
            {'user': users[1], 'total': 50},
            # Thêm nhiều giỏ hàng khác ở đây
        ]
        for cart in carts:
            Cart.objects.create(
                user=cart['user'],
                total=cart['total']
            )

    def seed_cart_details(self):
        carts = Cart.objects.all()
        details = [
            {'cart': carts[0],
             'product_detail': ProductDetail.objects.first(),
             'quantity': 1},
            {'cart': carts[1],
             'product_detail': ProductDetail.objects.last(),
             'quantity': 2},
            # Thêm nhiều chi tiết giỏ hàng khác ở đây
        ]
        for detail in details:
            CartDetail.objects.create(
                cart=detail['cart'],
                product_detail=detail['product_detail'],
                quantity=detail['quantity']
            )
