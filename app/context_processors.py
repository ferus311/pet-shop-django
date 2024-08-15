from django.db.models import Count
from .models import (
    Category,
    Species,
)


def global_context(request):
    return {
        "categories": Category.objects.annotate(
            num_products=Count("product")).order_by(
            "-num_products",
            "name"),
        "species": Species.objects.all(),
    }
