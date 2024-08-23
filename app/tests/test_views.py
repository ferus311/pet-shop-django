import unicodedata
import json
from unittest.mock import patch
from app.constants import CITIES
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from app.models import Cart, CartDetail, ProductDetail, Product, Category
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class SignUpTests(TestCase):

    def setUp(self):
        # Tạo dữ liệu người dùng để kiểm tra trùng lặp
        self.existing_user = User.objects.create_user(
            username='existing_user',
            email='existing@gmail.com',
            password='TestPassword123'
        )

    def test_signup_success(self):
        """Test đăng ký thành công với thông tin hợp lệ"""
        response = self.client.post(reverse('sign-up'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'new_user',
            'email': 'newuser@gmail.com',
            'password1': 'qwe123!@#',
            'password2': 'qwe123!@#',
            'default_phone_number': '0123456789',
            'default_address': '123 Main St'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_user').exists())

    def test_signup_missing_required_fields(self):
        """Test đăng ký với thông tin bị thiếu"""
        response = self.client.post(reverse('sign-up'), {
            'first_name': '',
            'last_name': '',
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
            'default_phone_number': '',
            'default_address': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'first_name',
                             'This field is required.')
        self.assertFormError(response, 'form', 'last_name',
                             'This field is required.')
        # Kiểm tra các field khác tương tự

    def test_signup_password_mismatch(self):
        """Test đăng ký với mật khẩu không khớp"""
        response = self.client.post(reverse('sign-up'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'new_user',
            'email': 'newuser@gmail.com',
            'password1': 'TestPassword123',
            'password2': 'DifferentPassword',
            'default_phone_number': '0123456789',
            'default_address': '123 Main St'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2',
                             "The two password fields didn’t match.")

    def test_signup_username_already_exists(self):
        """Test đăng ký với tên người dùng đã tồn tại"""
        response = self.client.post(reverse('sign-up'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'existing_user',
            'email': 'anotheremail@gmail.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'default_phone_number': '0123456789',
            'default_address': '123 Main St'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username',
                             'A user with that username already exists.')

    def test_signup_email_already_exists(self):
        """Test đăng ký với email đã tồn tại"""
        response = self.client.post(reverse('sign-up'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'new_user',
            'email': 'existing@gmail.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'default_phone_number': '0123456789',
            'default_address': '123 Main St'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email',
                             'A user with that email already exists.')

    def test_signup_invalid_phone_number(self):
        """Test đăng ký với số điện thoại không hợp lệ"""
        response = self.client.post(reverse('sign-up'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'new_user',
            'email': 'newuser@gmail.com',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'default_phone_number': '123123123123',
            'default_address': '123 Main St'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'default_phone_number', 'Ensure this value has at most 10 characters (it has 12).')

    def test_signup_invalid_email(self):
        """Test đăng ký với email không hợp lệ"""
        response = self.client.post(reverse('sign-up'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'new_user',
            'email': 'invalid_email',
            'password1': 'TestPassword123',
            'password2': 'TestPassword123',
            'default_phone_number': '1234567890',
            'default_address': '123 Main St'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email',
                             'Enter a valid email address.')


CustomUser = get_user_model()


class UpdateCartItemTests(TestCase):
    def setUp(self):
        # Tạo dữ liệu test
        self.user = CustomUser.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=100,
            average_rating=4.5,
            sold_quantity=10)
        self.product_detail = ProductDetail.objects.create(
            product=self.product, size='M', color='Red', price=100, remain_quantity=10)
        self.product_detail_new = ProductDetail.objects.create(
            product=self.product, size='L', color='Blue', price=150, remain_quantity=10)
        self.cart = Cart.objects.create(user=self.user, total=100)
        self.cart_detail = CartDetail.objects.create(
            cart=self.cart, product_detail=self.product_detail, quantity=1)
        self.client.login(username='testuser', password='12345')

    def test_update_cart_item_success(self):
        response = self.client.post(
            reverse('update_cart_item'),
            data=json.dumps({
                'item_id': self.cart_detail.id,
                'quantity': 2,
                'size': 'L',
                'color': 'Blue'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.cart_detail.refresh_from_db()
        self.assertEqual(self.cart_detail.product_detail.size, 'L')
        self.assertEqual(self.cart_detail.product_detail.color, 'Blue')
        self.assertEqual(self.cart_detail.quantity, 2)
        self.assertEqual(self.cart_detail.product_detail.price, 150)
        self.cart.refresh_from_db()
        expected_total = self.cart_detail.product_detail.price * self.cart_detail.quantity
        self.assertEqual(self.cart.total, expected_total)
        self.assertJSONEqual(response.content,
                             {'message': 'Cart item updated successfully'})

    def test_update_cart_item_product_detail_does_not_exist(self):
        response = self.client.post(
            reverse('update_cart_item'),
            data=json.dumps({
                'item_id': self.cart_detail.id,
                'quantity': 2,
                'size': 'XL',
                'color': 'Green'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content,
                             {'error': 'Product detail does not exist.'})

    def test_update_cart_item_exceeds_stock(self):
        response = self.client.post(
            reverse('update_cart_item'),
            data=json.dumps({
                'item_id': self.cart_detail.id,
                'quantity': 20,
                'size': 'L',
                'color': 'Blue'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content,
                             {'error': 'Quantity exceeds available stock.'})

    def test_update_cart_item_invalid_json(self):
        response = self.client.post(
            reverse('update_cart_item'),
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', json.loads(response.content))

    def test_update_cart_item_no_item_id(self):
        response = self.client.post(
            reverse('update_cart_item'),
            data=json.dumps({
                'quantity': 2,
                'size': 'L',
                'color': 'Blue'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', json.loads(response.content))


class RemoveCartItemTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=100,
            average_rating=4.5,
            sold_quantity=10)
        self.product_detail = ProductDetail.objects.create(
            product=self.product, size='M', color='Red', price=100, remain_quantity=10)
        self.cart = Cart.objects.create(user=self.user, total=100)
        self.cart_detail = CartDetail.objects.create(
            cart=self.cart, product_detail=self.product_detail, quantity=1)
        self.client.login(username='testuser', password='12345')

    def _normalize_address(self, address):
        address = address.lower()
        address = ''.join(
            c for c in unicodedata.normalize('NFD', address)
            if unicodedata.category(c) != 'Mn'
        )
        return address

    def _extract_city(self, address, cities):
        normalized_address = self._normalize_address(address)
        for city in cities:
            if city in normalized_address:
                return city
        return None

    def calculate_shipping_fee(self, user_city):
        if user_city in CITIES:
            return 15000
        else:
            return 25000

    def test_remove_cart_item_success(self):
        self.user_city = self._extract_city(self.user.default_address, CITIES)
        subtotal = 100
        shipping_fee = self.calculate_shipping_fee(self.user_city)
        expected_total_price = subtotal + shipping_fee

        response = self.client.post(
            reverse(
                'remove_cart_item', args=[
                    self.cart_detail.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            CartDetail.objects.filter(
                id=self.cart_detail.id).exists())
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.total, 0)
        expected_response = {
            'success': True,
            'quantity': 0,
            'removed': True,
            'subtotal': 0,
            'total_price': 0 + shipping_fee,
            'discount_fee': 0,
            'message': 'Please select a voucher again.'
        }
        self.assertJSONEqual(response.content, expected_response)

    def test_cart_item_does_not_exist(self):
        non_existent_id = 9999
        response = self.client.post(
            reverse(
                'remove_cart_item',
                args=[non_existent_id]))
        self.assertEqual(response.status_code, 200)
        expected_response = {
            'success': False,
            'error': 'An error occurred: No CartDetail matches the given query.'}
        self.assertJSONEqual(response.content, expected_response)

    @patch('app.views.get_object_or_404')
    def test_unexpected_exception(self, mock_get_object_or_404):
        mock_get_object_or_404.side_effect = Exception("Unexpected Error")

        response = self.client.post(
            reverse(
                'remove_cart_item', args=[
                    self.cart_detail.id]))
        self.assertEqual(response.status_code, 200)
        expected_response = {
            'success': False,
            'error': 'An error occurred: Unexpected Error'
        }
        self.assertJSONEqual(response.content, expected_response)
