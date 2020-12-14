from django.contrib import admin
from django.urls import path, include
from django.contrib.flatpages import views

urlpatterns = [
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("about/", include("django.contrib.flatpages.urls")),
    path("contacts/", views.flatpage, {"url": "/contacts/"}, name="contacts"),
    path("terms/", views.flatpage, {"url": "/terms/"}, name="terms"),
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path(
        'about-author/',
        views.flatpage,
        {'url': '/about-author/'},
        name='about_author'),
    path(
        'about-spec/',
        views.flatpage,
        {'url': '/about-spec/'},
        name='about_spec'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path("", include("posts.urls")),
]
