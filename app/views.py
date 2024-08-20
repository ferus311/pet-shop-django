import pyotp
import re
import unicodedata
import json
import os
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.contrib.auth import login, authenticate, get_user_model
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404, resolve_url
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import SignInForm, SignUpForm, SignUpForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal

from .models import *
from .forms import SignInForm, SignUpForm, OrderFilterForm
from .constants import DEFAULT_DISPLAY_CATEGORIES, PAGINATE_BY, CITIES

from django.db import transaction


def index(request):
    """View function for home page of site."""
    best_selling_products = Product.objects.all().order_by("-sold_quantity")

    default_display_category = list(
        Category.objects.filter(name__in=DEFAULT_DISPLAY_CATEGORIES)
    )
    needed_count = DEFAULT_DISPLAY_CATEGORIES.__len__() - len(default_display_category)
    if needed_count > 0:
        additional_categories = Category.objects.exclude(
            name__in=DEFAULT_DISPLAY_CATEGORIES).exclude(
            id__in=[
                c.id for c in default_display_category])[
                :needed_count]
        default_display_category.extend(additional_categories)

    products_by_category = {}
    for category in default_display_category:
        products_by_category[category] = Product.objects.filter(
            category=category)

    products_paginated = pagination(best_selling_products, request)
    context = {
        "best_selling_products": products_paginated,
        "products_by_category": products_by_category,
    }
    return render(request, "home.html", context=context)


def pagination(products, request):
    paginator = Paginator(products, PAGINATE_BY)
    page = request.GET.get("page")
    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)
    return products_paginated


def search_products(request):
    products = Product.objects.all()
    query = request.GET.get("query")
    results = products.order_by("-sold_quantity")
    if query:
        results = products.filter(
            Q(name__icontains=query)
            | Q(category__name__icontains=query)
            | Q(species__name__icontains=query)
        )
    results_list = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
        }
        for product in results
    ]
    return JsonResponse({'results': results_list}, safe=False)


def ShopView(request):
    """View function for shop page of site."""
    query = request.GET.get("query", "")
    sort_option = request.GET.get("sort", "name")
    selected_species = request.GET.getlist("species")
    selected_categories = request.GET.getlist("categories")
    price_max = request.GET.get("price_max")
    price_min = request.GET.get("price_min")

    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(category__name__icontains=query)
            | Q(species__name__icontains=query)
        )
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if selected_species:
        products = products.filter(species__id__in=selected_species)
    if selected_categories:
        products = products.filter(category__id__in=selected_categories)
    if sort_option == "price_asc":
        products = products.order_by("price")
    elif sort_option == "price_desc":
        products = products.order_by("-price")
    elif sort_option == "name":
        products = products.order_by("name")

    categories = Category.objects.all()

    products_paginated = pagination(products, request)

    context = {
        "categories": categories,
        "products": products_paginated,
        "query": query,
        "selected_species": selected_species,
        "selected_categories": selected_categories,
        "price_max": price_max,
        "price_min": price_min,
    }
    return render(request, "app/shop.html", context=context)


@login_required
def voucher_list(request):
    user = request.user
    vouchers = Voucher.objects.all()
    voucher_histories = VoucherHistory.objects.filter(user=user)
    current_year = timezone.now().year
    category_id = request.GET.get('category')
    if category_id:
        vouchers = vouchers.filter(
            models.Q(is_global=True) | models.Q(category__id=category_id)
        )

    min_discount = request.GET.get('min_discount')
    if min_discount:
        vouchers = vouchers.filter(discount__gte=min_discount)

    max_discount = request.GET.get('max_discount')
    if max_discount:
        vouchers = vouchers.filter(discount__lte=max_discount)
    vouchers_paginated = pagination(vouchers, request)
    voucher_histories_paginated = pagination(voucher_histories, request)

    context = {
        'vouchers': vouchers_paginated,
        'voucher_histories': voucher_histories_paginated,
        "current_year": current_year,
    }
    return render(request, 'app/voucher_list.html', context)


def clean_message(message):
    return re.sub("<[^<]+?>", "", str(message))


def login_view(request):
    next_url = request.POST.get('next', request.GET.get('next', '/'))
    if next_url:
        request.session['next_url'] = next_url
    if request.method == "POST":
        User = get_user_model()
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            try:
                user = User.objects.get(username=username)
                if not user.is_active:
                    messages.error(
                        request, _("Your account is inactive. Please verify your account."))
                    request.session['user_id'] = user.id
                    _send_otp_mail(user)
                    return redirect('verify-input')
            except User.DoesNotExist:
                user = None
            if user is not None:
                if user.is_active:
                    if user.is_banned:
                        messages.error(request, _(
                            "Your account has been banned."))
                    else:
                        auth_login(request, user)
                        messages.success(request, _(
                            "You have been logged in successfully."))
                        next_url = request.session.pop('next_url')
                        return redirect(next_url)
                else:
                    login(request, user)
                    messages.success(request, _(
                        "You have been logged in successfully."))
                    return redirect(next_url)
            else:
                messages.error(request, _("Invalid username or password."))
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignInForm()

    return render(request, 'registration/sign_in.html', {'form': form})


def get_price(request):
    if request.method == "GET":
        size = request.GET.get("size")
        color = request.GET.get("color")
        price = get_price_from_database(size, color)

        if price is not None:
            return JsonResponse({"price": price})
        else:
            return JsonResponse({"price": None})
    return JsonResponse({"error": "Invalid request method"}, status=400)


def get_available_options(request):
    if request.method == 'GET':
        available_sizes = ProductDetail.objects.values_list(
            'size', flat=True).distinct()
        available_colors = ProductDetail.objects.values_list(
            'color', flat=True).distinct()

        sizes = list(available_sizes)
        colors = list(available_colors)
        return JsonResponse({"sizes": sizes, "colors": colors})
    return JsonResponse({"error": "Invalid request method"}, status=400)


def get_price_from_database(size, color):
    try:
        product_detail = ProductDetail.objects.get(size=size, color=color)
        return product_detail.price
    except ProductDetail.DoesNotExist:
        return None


def product_detail_view(request, id):
    product = get_object_or_404(Product, pk=id)
    product_details = ProductDetail.objects.filter(product=product)
    average_rating = product.average_rating
    review_count = product.review_count
    sizes = product_details.values_list("size", flat=True).distinct()
    colors = product_details.values_list("color", flat=True).distinct()
    category = product.category
    comments = Comment.objects.filter(product=product).select_related("user")

    context = {
        "product": product,
        "category": category,
        "sizes": sizes,
        "colors": colors,
        "comments": comments,
        "average_rating": average_rating,
        "review_count": review_count,
    }
    return render(request, "app/product_detail.html", context)


def get_product_detail_id(request):
    size = request.GET.get('size')
    color = request.GET.get('color')
    product_id = request.GET.get('product_id')
    try:
        product_detail = ProductDetail.objects.get(
            product_id=product_id, size=size, color=color)
        return JsonResponse({'product_detail_id': product_detail.id})
    except ProductDetail.DoesNotExist:
        messages.error(request, _('Product type does not exist'))
        return JsonResponse({'error': 'Product detail not found'}, status=404)


@login_required
@require_POST
@csrf_exempt
def add_to_cart(request):
    quantity = int(request.POST.get('quantity', 1))
    product_detail_id = request.POST.get('product_detail_id')

    product_detail = ProductDetail.objects.get(id=product_detail_id)

    cart, created = Cart.objects.get_or_create(
        user=request.user, defaults={'total': 0})

    cart_details, created = CartDetail.objects.get_or_create(
        cart=cart,
        product_detail=product_detail,
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_details.quantity + quantity
    else:
        new_quantity = quantity

    if new_quantity > product_detail.remain_quantity:
        messages.error(request, _('Sorry, We have ran out of this type'))
        return JsonResponse({'success': False, 'message': _(
            'Sorry, We have ran out of this type')}, status=400)

    cart_details.quantity = new_quantity
    cart_details.save()

    cart.total += product_detail.price * quantity
    cart.save()

    cart_length = CartDetail.objects.filter(cart=cart).count()

    messages.success(request, _('Product added to cart successfully!'))
    return JsonResponse({'success': True,
                         'message': _('Product added to cart successfully!'),
                         'cart_length': cart_length})


def _send_otp_mail(user):
    otp = user.generate_otp()
    context = {
        'otp': otp,
        'user': user
    }
    subject = _('Your OTP Code')
    from_email = settings.EMAIL_HOST_USER
    to_email = user.email
    html_content = render_to_string(
        'registration/verify_message.html', context)
    text_content = f'Your OTP code is {otp}.'
    email = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        [to_email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                _("Account created successfully. Please check your email to activate your account."))
            _send_otp_mail(user=user)
            request.session['user_id'] = user.id
            return redirect('/verify-input')
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignUpForm()
    return render(request, 'registration/sign_up.html', {'form': form})


def verify_input(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, _("No user information found."))
        return redirect('login')
    user = CustomUser.objects.get(id=user_id)
    if request.method == 'POST':
        if 'resend_otp' in request.POST:
            _send_otp_mail(user)
            messages.success(request, _("OTP has been resent to your email."))
            return redirect('verify-input')
        otp_code = request.POST.get('otp', '')
        if user.is_otp_expired():
            messages.error(request, _(
                "OTP code has expired. Please choose resend OTP"))
            return redirect('verify-input')
        totp = pyotp.TOTP(user.otp_secret, interval=300)
        is_valid = totp.verify(otp_code)
        if is_valid:
            user.is_active = True
            user.save()
            messages.success(request, _("Your account has been activated."))
            del request.session['user_id']
            return redirect('sign-in')
        else:
            messages.error(request, _("Invalid OTP code."))
    return render(request, 'registration/verify_input.html')


def _normalize_address(address):
    address = address.lower()
    address = ''.join(
        c for c in unicodedata.normalize('NFD', address)
        if unicodedata.category(c) != 'Mn'
    )
    return address


def _extract_city(address, cities):
    normalized_address = _normalize_address(address)
    for city in cities:
        if city in normalized_address:
            return city
    return None


def _calculate_cart_totals(user):
    cart, created = Cart.objects.get_or_create(
        user=user, defaults={'total': 0})
    cart_items = CartDetail.objects.filter(cart=cart)
    for item in cart_items:
        item.total = item.product_detail.price * item.quantity

    subtotal = sum(
        item.product_detail.price *
        item.quantity for item in cart_items)

    user_city = _extract_city(user.default_address, CITIES)

    if user_city in CITIES:
        shipping_fee = 15000
    else:
        shipping_fee = 25000

    total_price = subtotal + shipping_fee

    return cart_items, subtotal, shipping_fee, total_price


@login_required
def cart_view(request):
    current_user = request.user
    cart_items, subtotal, shipping_fee, total_price = _calculate_cart_totals(
        current_user)
    sizes = set()
    colors = set()
    for item in cart_items:
        product_id = item.product_detail.product.id
        product = get_object_or_404(Product, pk=product_id)
        product_details = ProductDetail.objects.filter(product=product)
        sizes.update(product_details.values_list("size", flat=True).distinct())
        colors.update(
            product_details.values_list(
                "color", flat=True).distinct())

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total_price': total_price,
        'sizes': list(sizes),
        'colors': list(colors)
    }

    return render(request, 'app/cart.html', context)


@login_required
@require_POST
@transaction.atomic
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = data.get('quantity')
        quantity = int(quantity)
        size = data.get('size')
        color = data.get('color')

        cart = Cart.objects.get(user=request.user)
        cart_item = get_object_or_404(CartDetail, id=item_id, cart=cart)
        try:
            product_detail = ProductDetail.objects.get(
                product=cart_item.product_detail.product,
                size=size,
                color=color
            )
        except ProductDetail.DoesNotExist:
            messages.error(request, _('Product detail does not exist.'))
            return JsonResponse(
                {'error': _('Product detail does not exist.')}, status=400)

        if quantity > product_detail.remain_quantity:
            messages.error(request, _('Maximum product type available.'))
            return JsonResponse(
                {'error': _('Quantity exceeds available stock.')}, status=400)

        cart_item.quantity = quantity
        cart_item.product_detail = product_detail
        cart_item.save()

        cart = cart_item.cart
        cart.total = sum(item.product_detail.price *
                         item.quantity for item in cart.cartdetail_set.all())
        cart.save()

        return JsonResponse(
            {'message': _('Cart item updated successfully')}, status=200)
    except Exception as e:
        transaction.set_rollback(True)
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def checkout_view(request):
    cart_items, subtotal, shipping_fee, total_price = _calculate_cart_totals(
        request.user)
    OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total_price': total_price,
        "OPENCAGE_API_KEY": OPENCAGE_API_KEY,
    }
    return render(request, 'app/checkout.html', context=context)


@login_required
def place_order(request):
    if request.method == 'POST':
        user = request.user
        address = request.POST.get('default_user_address')
        payment_method = request.POST.get('payment_method')
        note_content = request.POST.get('text')

        if not address or not payment_method:
            messages.error(request, _("Please fill in all required fields."))
            return redirect('checkout')

        cart_items, subtotal, shipping_fee, total_price = _calculate_cart_totals(
            request.user)

        with transaction.atomic():
            try:
                bill = Bill.objects.create(
                    user=user,
                    address=address,
                    phone_number=user.default_phone_number,
                    payment_method=payment_method,
                    note_content=note_content,
                    total=Decimal(total_price),
                    status='Pending'
                )

                for item in cart_items:
                    BillDetail.objects.create(
                        bill=bill,
                        product_detail=item.product_detail,
                        quantity=item.quantity
                    )
                    item.delete()

                messages.success(
                    request, _("Your order has been placed successfully!"))

            except Exception as e:
                print(f"An error occurred: {e}")
                messages.error(
                    request, _("An error occurred while placing your order. Please try again."))
                return redirect('checkout')

        subject = _('Order Confirmation')
        from_email = settings.EMAIL_HOST_USER
        to_email = request.user.email
        message = render_to_string('registration/order_success.html', {
            'user': request.user,
            'order': bill,
            'order_items': cart_items,
        })
        email = EmailMessage(
            subject,
            message,
            from_email,
            [to_email],
        )
        email.content_subtype = 'html'
        email.send()

        return redirect('index')

    else:
        return redirect('checkout')


@login_required
@require_POST
@transaction.atomic
def update_quantity(request):
    item_id = request.POST.get('item_id')
    action = request.POST.get('action')

    try:
        cart_item = CartDetail.objects.get(id=item_id)
        cart = Cart.objects.get(id=cart_item.cart.id)
        product_detail = ProductDetail.objects.get(
            id=cart_item.product_detail.id)

        if action == 'increase':
            if cart_item.quantity < product_detail.remain_quantity:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(request, _('Maximum product type available.'))
                return JsonResponse({'success': False, 'error': _(
                    'Quantity exceeds available stock.')})
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
                cart_items, subtotal, shipping_fee, total_price = _calculate_cart_totals(
                    request.user)
                cart.total = subtotal
                cart.save()
                return JsonResponse(
                    {'success': True, 'quantity': 0, 'removed': True})
        new_total = cart_item.quantity * product_detail.price

        cart_items, subtotal, shipping_fee, total_price = _calculate_cart_totals(
            request.user)
        print(subtotal)
        cart.total = subtotal
        cart.save()
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'total': new_total,
            'subtotal': subtotal,
            'shipping_fee': shipping_fee,
            'total_price': total_price
        })
    except ProductDetail.DoesNotExist:
        return JsonResponse({'success': False,
                             'error': _('Product detail does not exist.')})
    except Exception as e:
        messages.error(request, _('An error occurred: ') + str(e))
        return JsonResponse({'success': False,
                             'error': _('An error occurred: ') + str(e)})


@login_required
@require_POST
def remove_cart_item(request, item_id):
    current_user = request.user
    try:
        cart_item = get_object_or_404(CartDetail, id=item_id)
        cart = Cart.objects.get(id=cart_item.cart.id)
        cart_item.delete()
        cart_items, subtotal, shipping_fee, total_price = _calculate_cart_totals(
            current_user)
        cart.total = subtotal
        cart.save()
        return JsonResponse({
            'success': True,
            'quantity': 0,
            'removed': True,
            'subtotal': subtotal,
            'total_price': total_price
        })
    except CartDetail.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': _('Cart item does not exist.')
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': _('An error occurred: ') + str(e)
        })


@login_required(login_url='/sign-in/')
def profile_view(request, pk):
    if pk == 0 or pk != request.user.pk:
        return redirect('profile', pk=request.user.pk)

    user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'app/profile.html', {'user': user})


@login_required
def submit_review(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        star = request.POST.get('star')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        product = Product.objects.get(id=product_id)

        Comment.objects.create(
            user=request.user,
            product=product,
            content=content,
            star=star,
        )

        messages.success(request, _('Thank you for reviewing the product!'))
        return redirect('purchased_products')


@login_required
def orders(request):
    user = request.user
    orders = Bill.objects.filter(user=user)
    context = {
        'orders': orders,
        'payment_status_choices': PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'app/order_tracking.html', context)


@login_required
def filter_orders(request):
    user = request.user
    form = OrderFilterForm(request.GET)
    if form.is_valid():
        orders = form.filter(user=user)
    else:
        orders = Bill.objects.filter(user=user)
    context = {
        'orders': orders,
        'form': form,
        'payment_status_choices': PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'app/order_tracking.html', context)
