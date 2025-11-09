"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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

# Importem configuracions, rutes i admin de Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


# Vista que redirigeix la pàgina principal '/' al login
def home_view(request):
    return redirect("users:login")


# Llista de rutes principals del projecte
urlpatterns = [
    # Ruta per accedir al panell d’administració de Django
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    path("users/", include("users.urls", namespace="users")),
]

# En mode desenvolupament, servim els fitxers media (avatars, imatges) des de MEDIA_URL
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
