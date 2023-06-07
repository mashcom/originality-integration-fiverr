from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("course/<int:id>", views.course, name="course"),
    path("course/<int:course_id>/assignment/<int:assignment_id>", views.course_assignments,
         name="submit_assignment"),
    path("turn_in", views.turn_in, name="turn_in"),
    path("reclaim_submission", views.reclaim_submission, name="reclaim_submission"),
    path("join", views.join_class, name="join_class")

]
