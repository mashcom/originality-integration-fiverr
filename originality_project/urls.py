from django.contrib import admin
from django.urls import include, path

from authentication import views

urlpatterns = [
    path("", views.index),
    path("auth", include("authentication.urls")),
    path("originality/", include("originality.urls")),
    path("api/v1/", include("api.urls")),
    path("admin/", admin.site.urls),
    path("config/", include("settings_manager.urls")),
    path("student/", include("student.urls")),
    path("teacher/", include("teacher.urls")),
    path('accounts/', include('allauth.urls')),
    path('setup/', include('setup.urls')),

]
