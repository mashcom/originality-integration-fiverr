from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("submit", views.submit_to_originality, name="submit_to_originality"),
    path("courses", views.course_list, name="course_list"),
    path("course_assignments/<str:course_id>", views.course_assignments, name="admin_course_assignments"),

    path("report/<str:course_id>/<str:assignment_id>", views.reports_for_teacher, name="reports_for_teacher"),
    path("report/student/<str:course_id>/<str:assignment_id>", views.reports_for_student, name="reports_for_student"),

    path("download/<str:originality_id>", views.download_report, name="download_report"),
    path("download/submission/<str:id>/<str:signature>", views.download_submission, name="download_submission"),
    path("external/download/submission/<str:file_id>/<str:signature>", views.external_download_submission,
         name="external_download_submission"),
    path("save_grade", views.save_grade, name="save_grade"),

]
