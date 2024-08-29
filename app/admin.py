from django.contrib import admin
from django.utils.html import format_html
from .forms import ProductForm, ProductDetailForm, BillForm, CustomUserForm, VoucherForm, VoucherHistoryForm
from .models import (
    CustomUser, Category, Product, ProductDetail, Bill, BillDetail,
    Comment, Voucher, VoucherHistory, Cart, CartDetail
)
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse

# Lớp SoftDeleteAdmin cho xóa mềm


class SoftDeleteAdmin(admin.ModelAdmin):
    list_display = ['is_deleted']

    def delete_view(self, request, object_id, extra_context=None):
        obj = get_object_or_404(self.model, pk=object_id)
        if request.method == "POST":
            # Perform the soft delete
            obj.is_deleted = True
            obj.save()
            # Add a success message
            messages.success(
                request,
                _("The selected %(object)s was soft deleted successfully.") % {
                    'object': str(obj)})
            # Redirect to the changelist page
            return redirect(
                reverse(
                    'admin:%s_%s_changelist' %
                    (self.opts.app_label, self.opts.model_name)))
        # If it's a GET request, display the confirmation page as usual
        return super().delete_view(request, object_id, extra_context=extra_context)

    actions = [_("soft_deleted"), _("recover_deleted")]

    @admin.action(description=_("Deleted all Selected Items Slightly"))
    def soft_deleted(self, request, queryset):
        queryset.update(is_deleted=True)

    @admin.action(description=_("Recover all Selected Items"))
    def recover_deleted(self, request, queryset):
        queryset.update(is_deleted=False)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserForm
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name')  # Thêm is_deleted
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('gender', )  # Thêm is_deleted vào bộ lọc
    # Sắp xếp theo is_deleted trước
    ordering = ('username', )

    def image_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 45px; height:45px;" />',
                obj.avatar.url)
        return "-"
    image_thumbnail.short_description = 'Image'


@admin.register(Category)
class CategoryAdmin(SoftDeleteAdmin):
    list_display = ('id', 'name', 'created_at', 'updated_at',
                    'is_deleted')  # Thêm is_deleted
    search_fields = ('name',)
    list_filter = ('is_deleted',)  # Thêm is_deleted vào bộ lọc
    ordering = ('is_deleted', 'name')  # Sắp xếp theo is_deleted trước


@admin.register(Product)
class ProductAdmin(SoftDeleteAdmin):
    form = ProductForm
    list_display = ('id', 'name', 'category', 'price',
                    'created_at', 'is_deleted')  # Thêm is_deleted
    search_fields = ('name', 'category__name')
    # Thêm is_deleted vào bộ lọc
    list_filter = ('category', 'is_deleted')
    ordering = ('is_deleted', 'name')  # Sắp xếp theo is_deleted trước


@admin.register(ProductDetail)
class ProductDetailAdmin(SoftDeleteAdmin):
    form = ProductDetailForm
    list_display = (
        'id',
        'product',
        'size',
        'color',
        'price',
        'remain_quantity',
        'created_at',
        'is_deleted')  # Thêm is_deleted
    search_fields = ('product__name', 'size', 'color')
    # Thêm is_deleted vào bộ lọc
    list_filter = ('size', 'color', 'is_deleted')
    ordering = ('is_deleted', 'product')  # Sắp xếp theo is_deleted trước


@admin.register(Bill)
class BillAdmin(SoftDeleteAdmin):
    form = BillForm
    list_display = (
        'id',
        'user',
        'address',
        'phone_number',
        'total',
        'status',
        'created_at',
        'is_deleted')  # Thêm is_deleted
    search_fields = ('user__username', 'address', 'phone_number')
    # Thêm is_deleted vào bộ lọc
    list_filter = ('status', 'payment_method', 'is_deleted')
    # Sắp xếp theo is_deleted trước
    ordering = ('is_deleted', 'created_at')


@admin.register(BillDetail)
class BillDetailAdmin(SoftDeleteAdmin):
    list_display = ('id', 'bill', 'product_detail', 'quantity',
                    'created_at', 'is_deleted')  # Thêm is_deleted
    search_fields = ('bill__user__username', 'product_detail__product__name')
    list_filter = ('is_deleted',)  # Thêm is_deleted vào bộ lọc
    ordering = ('is_deleted', 'bill')  # Sắp xếp theo is_deleted trước


@admin.register(Comment)
class CommentAdmin(SoftDeleteAdmin):
    list_display = ('id', 'user', 'product', 'content', 'star',
                    'created_at', 'is_deleted')  # Thêm is_deleted
    search_fields = ('user__username', 'product__name', 'content')
    list_filter = ('star', 'is_deleted')  # Thêm is_deleted vào bộ lọc
    # Sắp xếp theo is_deleted trước
    ordering = ('is_deleted', 'created_at')


@admin.register(Voucher)
class VoucherAdmin(SoftDeleteAdmin):
    form = VoucherForm
    list_display = (
        'id',
        'discount',
        'started_at',
        'ended_at',
        'is_global',
        'user',
        'created_at',
        'is_deleted')  # Thêm is_deleted
    search_fields = ('user__username',)
    # Thêm is_deleted vào bộ lọc
    list_filter = ('is_global', 'is_deleted')
    # Sắp xếp theo is_deleted trước
    ordering = ('is_deleted', 'created_at')


@admin.register(VoucherHistory)
class VoucherHistoryAdmin(SoftDeleteAdmin):
    form = VoucherHistoryForm
    list_display = ('id', 'user', 'voucher', 'is_deleted')  # Thêm is_deleted
    search_fields = ('user__username', 'voucher__id')
    list_filter = ('is_deleted',)  # Thêm is_deleted vào bộ lọc
    ordering = ('is_deleted', 'user')  # Sắp xếp theo is_deleted trước


@admin.register(Cart)
class CartAdmin(SoftDeleteAdmin):
    list_display = ('id', 'user', 'total', 'created_at',
                    'is_deleted')  # Thêm is_deleted
    search_fields = ('user__username',)
    list_filter = ('is_deleted',)  # Thêm is_deleted vào bộ lọc
    # Sắp xếp theo is_deleted trước
    ordering = ('is_deleted', 'created_at')


@admin.register(CartDetail)
class CartDetailAdmin(SoftDeleteAdmin):
    list_display = ('id', 'cart', 'product_detail', 'quantity',
                    'created_at', 'is_deleted')  # Thêm is_deleted
    search_fields = ('cart__user__username', 'product_detail__product__name')
    list_filter = ('is_deleted',)  # Thêm is_deleted vào bộ lọc
    ordering = ('is_deleted', 'cart')  # Sắp xếp theo is_deleted trước
