import re
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import SignInForm, SignUpForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import *
from django.http import JsonResponse
from .constants import DEFAULT_DISPLAY_CATEGORIES, PAGINATE_BY
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q


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


def clean_message(message):
    return re.sub("<[^<]+?>", "", str(message))


def login_view(request):
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    if user.is_banned:
                        messages.error(
                            request, _("Your account has been banned."))
                    else:
                        login(request, user)
                        messages.success(
                            request, _("You have been logged in successfully.")
                        )
                        return redirect("index")
                else:
                    request.session["user_id"] = user.id
                    return redirect(reverse("otp_verify"))
            else:
                messages.error(request, _("Invalid username or password."))
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignInForm()

    return render(request, "registration/sign_in.html", {"form": form})


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


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                _("Account created successfully. Please check your email to activate your account."))
            return redirect('/sign-in')
        else:
            for error in list(form.errors.values()):
                messages.error(request, clean_message(error))
    else:
        form = SignUpForm()

    return render(request, 'registration/sign_up.html', {'form': form})
