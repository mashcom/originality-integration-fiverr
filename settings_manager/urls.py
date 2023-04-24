from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("verify_key", views.verify_key, name="verify_key")
]
