"""django_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from application1 import views

urlpatterns = [
    url(r'uploads/simple', views.multiple_buttons, name='multiple_buttons'),
    path('', views.Home.as_view(), name='home'),
    path('points/', include('application1.urls', namespace='application1')),
    path('admin/', admin.site.urls),
    url(r'uploads/infected', views.post_infected_file, name='post_infected_file'),
    url(r'uploads/healthy', views.post_healthy_file, name='post_healthy_file'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)