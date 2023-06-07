from django.db import models
from django.utils import timezone

class Assignments(models.Model):
    id = models.BigAutoField(primary_key="id")
    title = models.TextField(max_length=250)
    course_id = models.TextField(max_length=50)
    assignment_id = models.TextField(max_length=50, default="")
    description = models.TextField(max_length=250)
    originality_check = models.TextField(max_length=2500)
    due_date = models.TextField(default="")
    due_time = models.TextField(default="")
    owner_id = models.TextField(max_length=100)
    processed = models.BooleanField(max_length=20, default=False)
    created_at = models.DateTimeField(default=timezone.now())
    resubmission_requested = models.DateTimeField(auto_now_add=True)

class AssignmentMaterials(models.Model):
    assignment_id = models.TextField(max_length=250)
    google_drive_id = models.TextField(max_length=250)

class AssignmentStudents(models.Model):
    id = models.BigIntegerField(primary_key="id")
    assignment_id = models.TextField(max_length=250)
    student_id = models.BigIntegerField()

class Courses(models.Model):
    id = models.BigAutoField(primary_key="id")
    course_id = models.TextField(max_length=50)
    name = models.TextField(max_length=250)
    description = models.TextField(max_length=250)
    owner_id = models.TextField(max_length=50)
