import datetime
import os.path
import uuid

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render, HttpResponse, redirect
from googleapiclient.errors import HttpError

from authentication import google
from services import google_classroom, originality
from teacher.models import Assignments, Courses, AssignmentMaterials
from django.contrib.auth.decorators import login_required
from originality_project.decorators import check_user_able_to_see_page

@login_required()
@check_user_able_to_see_page("teachers")
def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    courses = google_classroom.get_classes(uid)
    Courses.objects.filter(owner_id=uid).delete()
    for course in courses:
        new_course = Courses()
        new_course.course_id = course.get("id")
        new_course.name = course.get("name")
        new_course.description = ""  # course.get("description")
        new_course.owner_id = course.get("ownerId")
        new_course.save()
    return render(request, "courses.html", {"courses": courses})

@login_required()
@check_user_able_to_see_page("teachers")
def create_course(request):
    return render(request, "create_course.html")

@login_required()
@check_user_able_to_see_page("teachers")
def save_course(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    if request.method == "POST":
        name = request.POST["name"]
        course = google_classroom.create_class(name=name, owner_id=uid, uid=uid)
        print("result")
        print(str(course))
        print(type(course))
        if course == True:
            messages.add_message(request, messages.SUCCESS, course,
                                 "alert alert-success fw-bold")
            return redirect('/teacher')
        messages.add_message(request, messages.ERROR, course,
                             "alert alert-danger fw-bold")
        return redirect(request.META.get('HTTP_REFERER'))

@login_required()
@check_user_able_to_see_page("teachers")
def create_assignment(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    courses = Courses.objects.filter(owner_id=uid).order_by("name")
    return render(request, "create_assignment.html", {"courses": courses})

@login_required()
@check_user_able_to_see_page("teachers")
def show_assignments(request, course_id):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    assignments = google_classroom.classroom_get_course_work(course_id=course_id, uid=uid)
    print(assignments)
    course = google_classroom.classroom_get_course(course_id=course_id, uid=uid)
    return render(request, "assignments_for_course.html", {"course": course, "assignments": assignments})

@login_required()
@check_user_able_to_see_page("teachers")
def handle_uploaded_file(upload_file, uuid):
    new_file_name = uuid + "_" + upload_file.name
    root_path = settings.BASE_DIR, 'uploads/assignments/'
    with open(os.path.join(root_path) + new_file_name, 'wb+') as destination:
        for chunk in upload_file.chunks():
            destination.write(chunk)
    return os.path.join(root_path) + new_file_name

@login_required()
@check_user_able_to_see_page("teachers")
def save_assignment(request):
    if request.method == "POST":

        title = request.POST["title"]
        course_id = request.POST["course"]
        description = request.POST["description"]
        originality_enabled = request.POST["originality_enabled"]
        due_date = request.POST["due_date"]
        due_time = request.POST["due_time"]
        uid = SocialAccount.objects.filter(user=request.user)[0].uid

        assignment = Assignments()
        assignment.title = title
        assignment.course_id = course_id
        assignment.description = description
        assignment.originality_check = originality_enabled
        assignment.processed = False
        assignment.owner_id = uid
        assignment.due_date = due_date
        assignment.due_time = due_time

        if assignment.save() is None:
            print(assignment)
            files = request.FILES.getlist("files")
            for file in files:
                request_uuid = str(uuid.uuid4())
                uploaded = originality.handle_uploaded_file(upload_file=file, uuid=request_uuid,
                                                            folder="uploads/teacher_assignments/")
                if uploaded != False:
                    google_drive_id = google_classroom.upload_file(file_path=uploaded, file_name=file.name, uid=uid)
                    assignment_material = AssignmentMaterials()
                    assignment_material.assignment_id = assignment.id
                    assignment_material.google_drive_id = google_drive_id
                    assignment_material.save()

            # return HttpResponse("files")

            created = create_assignment_in_background(id=assignment.id, uid=uid)
            if created != False:
                messages.add_message(request, messages.SUCCESS,
                                     "Assignment created successfully!",
                                     "alert alert-success fw-bold")
                return redirect("/teacher/assignments/course/" + course_id)

            messages.add_message(request, messages.ERROR, created,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

        else:
            messages.add_message(request, messages.ERROR, "Assignment could not be created",
                                 "alert alert-danger fw-bold")

        return render(request, "create_assignment.html")
    return HttpResponse("Invalid request method")

@login_required()
@check_user_able_to_see_page("teachers")
def create_assignment_in_background(id, uid):
    assignment = get_object_or_404(Assignments, id=id)
    due_date = assignment.due_date
    date = datetime.datetime.strptime(due_date, "%m/%d/%Y")
    due_time = assignment.due_time
    due_time_process = datetime.datetime.strptime(due_time, "%H:%M")

    materials = []

    assignment_materials = AssignmentMaterials.objects.filter(assignment_id=assignment.id)
    for material in assignment_materials:
        materials.append({
            "driveFile": {
                "driveFile": {
                    "id": material.google_drive_id
                }
            }
        }, )

    print(materials)

    try:
        service = google.get_google_service_instance(uid=uid)
        coursework = {
            'title': assignment.title,
            'description': assignment.description,
            'materials': materials,
            'workType': 'ASSIGNMENT',
            'state': 'PUBLISHED',
            'dueDate': {
                "year": date.year,
                "month": date.month,
                "day": date.day
            },
            "dueTime": {
                "hours": due_time_process.hour,
                "minutes": due_time_process.minute,
            }

        }
        coursework = service.courses().courseWork().create(courseId=assignment.course_id, body=coursework).execute()
        print(f"Assignment created with ID {coursework.get('id')}")
        assignment.assignment_id = coursework.get('id')
        assignment.processed = 1
        assignment.save()
        return coursework.get("id")

    except HttpError as error:
        print('An errors occurred: %s' % error)
        return False
