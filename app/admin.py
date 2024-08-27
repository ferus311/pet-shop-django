from django.contrib import admin
from django.utils.html import format_html
from .forms import ProductForm, ProductDetailForm, BillForm, CustomUserForm, VoucherForm, VoucherHistoryForm
from .models import (
    CustomUser, Category, Product, ProductDetail, Bill, BillDetail,
    Comment, Voucher, VoucherHistory, Cart, CartDetail
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'gender', 'image_thumbnail')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('gender',)
    ordering = ('username',)
    list_per_page = 2  # Constant

    def image_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 45px; height:45px;" />',
                obj.avatar.url)
        return "-"
    image_thumbnail.short_description = 'Image'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('id', 'name', 'category', 'price', 'created_at')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    ordering = ('name',)


@admin.register(ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    form = ProductDetailForm
    list_display = ('id', 'product', 'size', 'color', 'price',
                    'remain_quantity', 'created_at')
    search_fields = ('product__name', 'size', 'color')
    list_filter = ('size', 'color')
    ordering = ('product',)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    form = BillForm
    list_display = ('id', 'user', 'address', 'phone_number',
                    'total', 'status', 'created_at')
    search_fields = ('user__username', 'address', 'phone_number')
    list_filter = ('status', 'payment_method')
    ordering = ('created_at',)


@admin.register(BillDetail)
class BillDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'bill', 'product_detail', 'quantity', 'created_at')
    search_fields = ('bill__user__username', 'product_detail__product__name')
    ordering = ('bill',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'content', 'star', 'created_at')
    search_fields = ('user__username', 'product__name', 'content')
    list_filter = ('star',)
    ordering = ('created_at',)


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    form = VoucherForm
    list_display = ('id', 'discount', 'started_at', 'ended_at',
                    'is_global', 'user', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('is_global',)
    ordering = ('created_at',)


@admin.register(VoucherHistory)
class VoucherHistoryAdmin(admin.ModelAdmin):
    form = VoucherHistoryForm
    list_display = ('id', 'user', 'voucher')
    search_fields = ('user__username', 'voucher__id')
    ordering = ('user',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'created_at')
    search_fields = ('user__username',)
    ordering = ('created_at',)


@admin.register(CartDetail)
class CartDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product_detail', 'quantity', 'created_at')
    search_fields = ('cart__user__username', 'product_detail__product__name')
    ordering = ('cart',)
