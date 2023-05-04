from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("course/<int:id>", views.course, name="course"),
    path("course/<int:course_id>/assignment/<int:assignment_id>", views.course_assignments,
         name="submit_assignment"),
    # path("originality", views.submit_to_originality, name="submit_to_originality"),

]
