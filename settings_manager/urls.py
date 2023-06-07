from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("verify_key", views.verify_key, name="verify_key"),
    path("log", views.log, name="log"),
    path("google_classroom", views.google_classroom_settings, name="google_classroom_settings"),
    path("health", views.check_file_system, name="check_file_system"),

]

admin.site.site_header = 'Originality Super Admin'  # default: "Django Administration"
admin.site.index_title = 'Originality'  # default: "Site administration"
admin.site.site_title = 'Site Admin'  # default: "Django site admin"
