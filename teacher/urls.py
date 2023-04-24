from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("assignment/create", views.create_assingment, name="create_assignment"),
    path("assignment", views.save_assignment, name="save_assignment")
]
