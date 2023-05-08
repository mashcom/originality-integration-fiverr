from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("submit", views.submit_to_originality, name="submit_to_originality"),
    path("report/<str:course_id>/<str:assignment_id>", views.reports_for_teacher, name="reports_for_teacher"),
    path("download/<str:originality_id>", views.download_report, name="download_report"),
    path("download/submission/<str:id>", views.download_submission, name="download_submission")

]
