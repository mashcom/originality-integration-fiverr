from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("submit", views.submit_to_originality, name="submit_to_originality"),
    path("report/<int:courseid>/<int:assignment_id>", views.reports_for_teacher, name="reports_for_teacher", )

]
