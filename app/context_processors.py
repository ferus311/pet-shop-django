from django.db.models import Count
from .models import (
    Category,
    Species,
    CartDetail
)


def global_context(request):
    context = {
        "categories": Category.objects.annotate(
            num_products=Count("product")).order_by(
            "-num_products",
            "name"),
        "species": Species.objects.all(),
    }

    if request.user.is_authenticated:
        user = request.user
        context["user"] = user
        context["num_cart_items"] = CartDetail.objects.filter(
            cart__user=request.user).count()
    else:
        context["num_cart_items"] = 0

    return context
