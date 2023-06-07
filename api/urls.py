from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("report", views.report, name="report"),
    path("report/plagiarism/originality/report.php", views.report, name="report_alternative"),
]
