from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("assignment/create", views.create_assignment, name="create_assignment"),
    path("assignment", views.save_assignment, name="save_assignment"),
    path("assignments/course/<int:course_id>", views.show_assignments, name="show_assignments_for_course")
]
