"""
URL configuration for pet_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.urls import include
from django.views.generic import RedirectView
from pet_shop import settings
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    path("i18n/setlang/", set_language, name="set_language"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
