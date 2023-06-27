from django.db import models

class Submission(models.Model):
    id = models.BigAutoField(primary_key="id")
    file_name = models.TextField(max_length=250, default="")
    sender_ip = models.TextField(max_length=250, default="")
    faculty_code = models.TextField(max_length=20, default="")
    faculty_name = models.TextField(max_length=50, default="")
    dept_code = models.TextField(max_length=50, default="")
    dept_name = models.TextField(max_length=50, default="")
    course_category = models.TextField(max_length=50, default="")
    course_code = models.TextField(max_length=50, default="")
    course_name = models.TextField(max_length=100, default="")
    assignment_code = models.TextField(max_length=50, default="")
    moodle_assign_page_no = models.TextField(max_length=50, default="")
    student_code = models.TextField(max_length=50, default="")
    owner_id = models.TextField(max_length=50, default="")
    lecturer_code = models.TextField(max_length=50, default="")
    group_members = models.TextField(max_length=50, default="")
    doc_sequence = models.TextField(max_length=50, default=1)
    file = models.TextField(default="")
    ghost_writer_check = models.TextField(max_length=10, default="")
    link_moodle_file = models.TextField(max_length=250, default="")
    gov_student_id_md5 = models.TextField(max_length=250, default="")
    google_classroom_id = models.TextField(max_length=100, default="")
    google_file_id = models.TextField(max_length=100, default="")
    originality_id = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Report(models.Model):
    id = models.BigAutoField(primary_key="id")
    file = models.TextField(default="")
    file_name = models.TextField(default="")
    grade = models.TextField(max_length=20, default="")
    user_id = models.TextField(default="")
    assignment_id = models.TextField(default="")
    doc_sequence = models.TextField(default="")
    ghostwrite_report = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Grade(models.Model):
    id = models.BigAutoField(primary_key="id")
    grade = models.TextField(max_length=20, default="")
    total_possible = models.TextField(max_length=20, default="")
    user_id = models.TextField(default="")
    assignment_id = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)