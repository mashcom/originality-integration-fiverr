from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("course/create", views.create_course, name="create_course"),
    path("course/<int:course_id>/edit", views.edit_course, name="edit_course"),
    path("course", views.save_course, name="save_course"),

    path("assignment/create", views.create_assignment, name="create_assignment"),
    path("assignment", views.save_assignment, name="save_assignment"),
    path("assignments/course/<int:course_id>", views.show_assignments, name="show_assignments_for_course"),

    path("assignments/course/<int:course_id>/assignmemt/<str:assignment_id>/edit", views.edit_assignment,
         name="edit_assignment"),
    path("toggle_originality/<str:assignment_id>", views.toggle_originality, name="toggle_originality"),

    path("delete_assignment", views.delete_assignment, name="delete_assignment"),
    path("delete_course", views.delete_course, name="delete_course"),

]
