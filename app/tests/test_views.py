import unicodedata
import json
from unittest.mock import patch
from app.constants import CITIES
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.urls import reverse
from app.models import *
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
            response,
            'form',
            'default_phone_number',
            'Ensure this value has at most 10 characters (it has 12).')

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


class GetAvailableVouchersTests(TestCase):
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
        self.voucher = Voucher.objects.create(
            discount=20,
            min_amount=50.0,
            started_at=timezone.localtime() - timezone.timedelta(days=1),
            ended_at=timezone.localtime() + timezone.timedelta(days=1),
            is_global=True
        )
        self.voucher.category.add(self.category)
        self.client.login(username='testuser', password='12345')

    def test_get_available_vouchers_success(self):
        response = self.client.get(reverse('get_available_vouchers'))
        self.assertEqual(response.status_code, 200)
        vouchers = response.json()['vouchers']
        self.assertEqual(len(vouchers), 1)
        self.assertEqual(vouchers[0]['id'], self.voucher.id)
        self.assertEqual(vouchers[0]['discount'], 20)
        self.assertEqual(vouchers[0]['min_amount'], 50.0)
        self.assertTrue('Test Category' in vouchers[0]['categories'])

    def test_no_vouchers_due_to_min_amount(self):
        self.voucher.min_amount = 1000.0
        self.voucher.save()

        response = self.client.get(reverse('get_available_vouchers'))
        self.assertEqual(response.status_code, 200)
        vouchers = response.json()['vouchers']
        self.assertEqual(len(vouchers), 0)

    def test_voucher_history_exclusion(self):
        VoucherHistory.objects.create(user=self.user, voucher=self.voucher)

        response = self.client.get(reverse('get_available_vouchers'))
        self.assertEqual(response.status_code, 200)
        vouchers = response.json()['vouchers']
        self.assertEqual(len(vouchers), 0)


class VoucherListViewTests(TestCase):
    def setUp(self):
        # Tạo người dùng
        self.user = CustomUser.objects.create_user(
            username='testuser', password='12345')
        self.client = Client()
        self.client.login(username='testuser', password='12345')

        # Tạo danh mục
        self.category_cat = Category.objects.create(name='Cat')
        self.category_dog = Category.objects.create(name='Dog')

        # Tạo sản phẩm và chi tiết sản phẩm
        self.product_cat = Product.objects.create(
            name='Cat Food',
            category=self.category_cat,
            price=100,
            average_rating=4.5)
        self.product_detail_cat = ProductDetail.objects.create(
            product=self.product_cat, size='M', color='Red', price=100, remain_quantity=10)

        self.product_dog = Product.objects.create(
            name='Dog Food',
            category=self.category_dog,
            price=150,
            average_rating=4.0)
        self.product_detail_dog = ProductDetail.objects.create(
            product=self.product_dog, size='L', color='Blue', price=150, remain_quantity=5)

        # Tạo giỏ hàng và chi tiết giỏ hàng
        self.cart = Cart.objects.create(user=self.user, total=100)
        self.cart_detail_cat = CartDetail.objects.create(
            cart=self.cart, product_detail=self.product_detail_cat, quantity=1)
        self.cart_detail_dog = CartDetail.objects.create(
            cart=self.cart, product_detail=self.product_detail_dog, quantity=1)

        self.voucher1 = Voucher.objects.create(
            discount=10,
            min_amount=50.0,
            started_at=timezone.localtime() - timezone.timedelta(days=10),
            ended_at=timezone.localtime() + timezone.timedelta(days=10),
            is_global=True
        )
        self.voucher1.category.add(self.category_cat)

        self.voucher2 = Voucher.objects.create(
            discount=20,
            min_amount=50.0,
            started_at=timezone.localtime() - timezone.timedelta(days=20),
            ended_at=timezone.localtime() - timezone.timedelta(days=5),
            is_global=True
        )
        self.voucher2.category.add(self.category_dog)

        self.voucher_history = VoucherHistory.objects.create(
            user=self.user, voucher=self.voucher1)

    def test_voucher_list_view(self):
        response = self.client.get(reverse('voucher_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/voucher_list.html')
        self.assertIn('vouchers', response.context)
        self.assertIn('voucher_histories', response.context)

    def test_voucher_list_view_with_category_filter(self):
        response = self.client.get(
            reverse('voucher_list'), {
                'category': self.category_cat.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['vouchers']), 1)
        self.assertEqual(response.context['vouchers'][0], self.voucher1)

    def test_voucher_list_view_with_min_discount_filter(self):
        response = self.client.get(
            reverse('voucher_list'), {
                'min_discount': 15})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['vouchers']), 1)
        self.assertEqual(response.context['vouchers'][0], self.voucher2)

    def test_voucher_list_view_with_max_discount_filter(self):
        response = self.client.get(
            reverse('voucher_list'), {
                'max_discount': 15})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['vouchers']), 1)
        self.assertEqual(response.context['vouchers'][0], self.voucher1)

    def test_voucher_list_view_with_voucher_status_filter(self):
        response = self.client.get(
            reverse('voucher_list'), {
                'voucher_status': 'EXPIRED'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['vouchers']), 1)
        self.assertEqual(response.context['vouchers'][0], self.voucher2)

        response = self.client.get(
            reverse('voucher_list'), {
                'voucher_status': 'USABLE'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['vouchers']), 1)
        self.assertEqual(response.context['vouchers'][0], self.voucher1)

        response = self.client.get(
            reverse('voucher_list'), {
                'voucher_status': 'UPCOMING'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['vouchers']), 0)

        response = self.client.get(
            reverse('voucher_list'), {
                'voucher_status': 'USED'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['vouchers']), 1)
        self.assertEqual(response.context['vouchers'][0], self.voucher1)


class UpdateQuantityTest(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_update_quantity_success(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('update_quantity'), {
            'item_id': self.cart_detail.id,
            'action': 'update_quantity',
            'quantity': 5
        })
        self.cart_detail.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.cart_detail.quantity, 5)

    def test_update_quantity_exceeds_stock(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('update_quantity'), {
            'item_id': self.cart_detail.id,
            'action': 'update_quantity',
            'quantity': 15
        })
        self.cart_detail.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.cart_detail.quantity,
            1)  # Quantity should not change
        self.assertContains(response, 'Quantity exceeds available stock.')

    def test_update_quantity_remove_item(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('update_quantity'), {
            'item_id': self.cart_detail.id,
            'action': 'update_quantity',
            'quantity': 0
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            CartDetail.objects.filter(
                id=self.cart_detail.id).exists())

    def test_update_quantity_invalid_item(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('update_quantity'), {
            'item_id': 9999,  # Non-existent item ID
            'action': 'update_quantity',
            'quantity': 5
        })
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            'Product detail does not exist',
            response.content.decode())


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            name='Test Product 1',
            category=self.category,
            price=100,
            average_rating=4.5,
            sold_quantity=10)
        self.product2 = Product.objects.create(
            name='Test Product 2',
            category=self.category,
            price=200,
            average_rating=4.0,
            sold_quantity=5)
        self.product_detail1 = ProductDetail.objects.create(
            product=self.product1, size='M', color='Red', price=100, remain_quantity=10)
        self.product_detail2 = ProductDetail.objects.create(
            product=self.product2, size='L', color='Blue', price=200, remain_quantity=5)
        self.cart = Cart.objects.create(user=self.user, total=300)
        self.cart_detail1 = CartDetail.objects.create(
            cart=self.cart, product_detail=self.product_detail1, quantity=1)
        self.cart_detail2 = CartDetail.objects.create(
            cart=self.cart, product_detail=self.product_detail2, quantity=1)
        self.client.login(username='testuser', password='12345')

    def test_cart_view(self):
        response = self.client.get(reverse('cart'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/cart.html')

        # Check context data
        self.assertIn('cart_items', response.context)
        self.assertIn('subtotal', response.context)
        self.assertIn('shipping_fee', response.context)
        self.assertIn('total_price', response.context)
        self.assertIn('product_details_dict', response.context)
        self.assertIn('has_out_of_stock', response.context)

        cart_items = response.context['cart_items']
        self.assertEqual(len(cart_items), 2)

        product_details_dict = response.context['product_details_dict']
        self.assertIn(self.product1.id, product_details_dict)
        self.assertIn(self.product2.id, product_details_dict)
        self.assertEqual(
            product_details_dict[self.product1.id]['sizes'], ['M'])
        self.assertEqual(
            product_details_dict[self.product1.id]['colors'], ['Red'])
        self.assertEqual(
            product_details_dict[self.product2.id]['sizes'], ['L'])
        self.assertEqual(
            product_details_dict[self.product2.id]['colors'], ['Blue'])

        has_out_of_stock = response.context['has_out_of_stock']
        self.assertFalse(has_out_of_stock)


class SubmitReviewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=100,
            average_rating=4.5,
            sold_quantity=10
        )
        self.product_detail = ProductDetail.objects.create(
            product=self.product, size='M', color='Red', price=100, remain_quantity=10)
        self.bill = Bill.objects.create(user=self.user, total=100.00)
        self.bill_detail = BillDetail.objects.create(
            bill=self.bill, product_detail=self.product_detail, quantity=1
        )
        self.client.login(username='testuser', password='12345')
        self.url = reverse('submit_review', args=[self.bill.id])

    def test_submit_review_success(self):
        response = self.client.post(self.url, {
            'product_id': self.product.id,
            'star': 5,
            'content': 'Great product!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Comment.objects.filter(
                user=self.user,
                product=self.product).exists())

    def test_submit_review_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url, {
            'product_id': self.product.id,
            'star': 5,
            'content': 'Great product!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Comment.objects.filter(
                user=self.user,
                product=self.product).exists())

    def test_submit_review_invalid_product(self):
        response = self.client.post(self.url, {
            'product_id': 999,  # Invalid product ID
            'star': 5,
            'content': 'Great product!',
        })
        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            Comment.objects.filter(
                user=self.user,
                product_id=999).exists())


class DeleteAccountTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        self.client.login(username='testuser', password='testpassword')

        self.bill = Bill.objects.create(
            user=self.user,
            address='123 Test St',
            phone_number='0123456789',
            total=100,
            status='Pending',
            payment_method='Credit Card'
        )

        # Tạo đối tượng Voucher
        self.voucher = Voucher.objects.create(
            discount=10.0,
            started_at=timezone.now(),
            ended_at=timezone.now() + timedelta(days=30),
            is_global=True
        )

        self.voucher_history = VoucherHistory.objects.create(
            user=self.user,
            voucher=self.voucher
        )

        self.cart = Cart.objects.create(
            user=self.user,
            total=50.0
        )

    def test_delete_account_success(self):
        response = self.client.post(
            reverse('delete_account'), {
                'password': 'testpassword'})
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_deleted)
        self.assertEqual(self.user.first_name, 'Deleted')
        self.assertEqual(self.user.last_name, 'User')
        self.assertTrue(self.user.username.startswith('deleted_user_'))
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(Bill.objects.filter(user=self.user).exists())
        self.assertFalse(
            VoucherHistory.objects.filter(
                user=self.user).exists())
        self.assertFalse(Cart.objects.filter(user=self.user).exists())

    def test_delete_account_invalid_password(self):
        response = self.client.post(
            reverse('delete_account'), {
                'password': 'wrongpassword'})
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_deleted)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile', args=[self.user.pk]))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]),
                         "Invalid password. Please try again.")

    def test_deleted_user_cannot_login(self):
        self.client.post(
            reverse('delete_account'), {
                'password': 'testpassword'})
        self.user.refresh_from_db()

        login_response = self.client.post(reverse('sign-in'), {
            'username': 'testuser',
            'password': 'testpassword'
        })

        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(login_response, "Invalid username or password.")
