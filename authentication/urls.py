from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("authenticate", views.attempt, name="authenticate"),
    path("no_group", views.no_group, name="no_group"),
    path("oauth_callback", views.oauth_callback, name="oauth_callback"),
]
