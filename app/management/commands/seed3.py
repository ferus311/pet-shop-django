from django.utils import timezone
from datetime import timedelta
from app.models import CustomUser, Category, Product, Species, ProductDetail, Bill, BillDetail, Comment, Voucher, VoucherHistory, Cart, CartDetail


def create_test_data():
    # Create a user
    user = CustomUser.objects.create_user(
        username='testuser',
        email='testuser@gmail.com',
        first_name='Test',
        last_name='User',
        default_address='123 Test Street',
        default_phone_number='0123456789',
        password='password123'
    )

    # Create Categories
    categories = [
        Category.objects.create(
            name=f'Category {i}') for i in range(
            1, 6)]

    # Create Species
    species_list = [
        Species.objects.create(
            name=f'Species {i}') for i in range(
            1, 6)]

    # Create Products and ProductDetails
    products = []
    for i in range(1, 6):
        product = Product.objects.create(
            name=f'Product {i}',
            category=categories[i % len(categories)],
            description=f'This is a description of product {i}.',
            average_rating=4.5,
        )
        products.append(product)
        product.species_set.add(species_list[i % len(species_list)])

        for size in ['S', 'M', 'L']:
            ProductDetail.objects.create(
                product=product,
                size=size,
                color='Red',
                price=100000 + i * 5000,
                remain_quantity=10
            )

    # Create a Voucher
    voucher = Voucher.objects.create(
        discount=10.0,
        started_at=timezone.now(),
        ended_at=timezone.now() + timedelta(days=10),
        is_global=False,
        user=user
    )
    voucher.category.set(categories)

    # Create a Bill
    bill = Bill.objects.create(
        user=user,
        address=user.default_address,
        phone_number=user.default_phone_number,
        status='paid',
        total=500000,
        payment_method='credit_card',
        expired_at=timezone.now() + timedelta(days=3)
    )

    # Create BillDetails
    for product in products:
        product_detail = product.productdetail_set.first()
        BillDetail.objects.create(
            bill=bill,
            product_detail=product_detail,
            quantity=1
        )

    # Create Comments
    for product in products:
        Comment.objects.create(
            user=user,
            product=product,
            content=f'This is a comment for {product.name}.',
            star=5
        )

    # Create Voucher History
    VoucherHistory.objects.create(
        user=user,
        voucher=voucher
    )

    # Create a Cart and CartDetails
    cart = Cart.objects.create(
        user=user,
        total=300000
    )

    for product in products:
        product_detail = product.productdetail_set.first()
        CartDetail.objects.create(
            cart=cart,
            product_detail=product_detail,
            quantity=1
        )

    print(f'User {user.username} created with related data.')


# Run the function to create the test data
create_test_data()
