from django.urls import path

from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("add_institution", views.add_institution, name="add_institution"),
    path("users", views.tenant_users, name="tenant_users"),
]
