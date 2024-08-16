import pyotp
import re
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import login, authenticate, get_user_model
from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils import timezone

from .models import *
from .forms import SignInForm, SignUpForm
from .constants import DEFAULT_DISPLAY_CATEGORIES, PAGINATE_BY


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
    next_url = request.GET.get('next', reverse('index'))
    if request.method == 'POST':
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
                if user.is_banned:
                    messages.error(request, _("Your account has been banned."))
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
        "review_count": review_count,  # Sử dụng review_count từ property
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
