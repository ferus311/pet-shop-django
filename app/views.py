from django.shortcuts import render


def index(request):
    """View function for home page of site."""
    return render(request, "home.html")


def ShopView(request):
    """View function for shop page of site."""
    return render(request, "app/shop.html")
