from django.test import TestCase
from django.urls import reverse
from app.models import Product, ProductDetail, Cart, CartDetail, CustomUser, Category


class AddToCartViewTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        self.category = Category.objects.create(name="Test Category")

        self.product = Product.objects.create(name="Test Product", category=self.category, average_rating=0.0)
        self.product_detail = ProductDetail.objects.create(
            product=self.product,
            size='M',
            color='Red',
            price=100,
            remain_quantity=10
        )

        self.cart = Cart.objects.create(user=self.user, total=0.0)

        self.add_to_cart_url = reverse('add_to_cart')

    def test_add_product_to_cart_successfully(self):
        response = self.client.post(self.add_to_cart_url, {
            'product_detail_id': self.product_detail.id,
            'quantity': 1
        })

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'success': True,
            'message': 'Product added to cart successfully!',
            'cart_length': 1
        })

        cart_detail = CartDetail.objects.filter(cart=self.cart, product_detail=self.product_detail).first()
        self.assertIsNotNone(cart_detail)
        self.assertEqual(cart_detail.quantity, 1)

        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total, 100)

    def test_add_product_exceeding_stock(self):
        response = self.client.post(self.add_to_cart_url, {
            'product_detail_id': self.product_detail.id,
            'quantity': 20
        })

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            'success': False,
            'message': 'Sorry, We have ran out of this type'
        })

        cart_detail = CartDetail.objects.filter(cart=self.cart, product_detail=self.product_detail).first()
        self.assertIsNone(cart_detail)

        self.product_detail.refresh_from_db()
        self.assertEqual(self.product_detail.remain_quantity, 10)
