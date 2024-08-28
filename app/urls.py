from django.urls import path, include
from .views import *

urlpatterns = [
    path(
        '',
        index,
        name='index'),
    path(
        'shop/',
        ShopView,
        name='shop'),
    path(
        'sign-in/',
        login_view,
        name="sign-in"),
    path(
        'sign-up/',
        signup_view,
        name="sign-up"),
    path(
        '',
        include('django.contrib.auth.urls')),
    path(
        'product/<int:id>/',
        product_detail_view,
        name='product_detail'),
    path(
        'get-price/',
        get_price,
        name='get_price'),
    path(
        'get-available-options/',
        get_available_options,
        name='get_available_options'),
    path(
        'get-product-detail-id/',
        get_product_detail_id,
        name='get_product_detail_id'),
    path(
        'search-products/',
        search_products,
        name='search_products'),
    path(
        'add-to-cart/',
        add_to_cart,
        name='add_to_cart'),
    path(
        'cart/',
        cart_view,
        name='cart'),
    path(
        'update-cart-item/',
        update_cart_item,
        name='update_cart_item'),
    path(
        'update-quantity/',
        update_quantity,
        name='update_quantity'),
    path(
        'cart/remove/<int:item_id>/',
        remove_cart_item,
        name='remove_cart_item'),
    path(
        'verify-input/',
        verify_input,
        name="verify-input"),
    path(
        'vouchers/',
        voucher_list,
        name='voucher_list'),
    path('apply_voucher/',
         apply_voucher,
         name='apply_voucher'),
    path('get_available_vouchers/',
         get_available_vouchers,
         name='get_available_vouchers'),
    path(
        'profile/<int:pk>/',
        profile_view,
        name='profile'),
    path(
        'orders/',
        orders,
        name='orders'),
    path(
        'orders/filter',
        filter_orders,
        name='filter_orders'),
    path('orders/cancel/<int:order_id>/',
         cancel_order,
         name='cancel_order'),
    path('order/<int:order_id>/',
         order_detail,
         name='order_detail'),
    path(
        'checkout/',
        checkout_view,
        name='checkout'),
    path(
        'place_order/',
        place_order,
        name='place_order'),
    path(
        'profile/update/',
        update_profile,
        name='update-profile'),
    path(
        'profile/update-avatar/',
        update_avatar,
        name='update-avatar'),
    path(
        'change-password/',
        change_password,
        name='change-password'),
    path(
        'order/<int:order_id>/submit_review/',
        submit_review,
        name='submit_review'),
    path(
        'get-options-for-cart-modal/',
        get_options_for_cart_modal,
        name='get_options_for_cart_modal'),
    path(
        'update-shipping-fee/',
        calculate_shipping_fee,
        name='update_shipping_fee'),
]
