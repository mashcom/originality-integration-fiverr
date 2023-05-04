from django.shortcuts import render, HttpResponse
from django.contrib import messages
from authentication import google
from teacher.models import AssignmentMaterials, AssignmentStudents, Assignments, Courses
from django.shortcuts import get_object_or_404
from services import google_classroom, originality
from allauth.socialaccount.models import SocialAccount
from googleapiclient.errors import HttpError

def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    courses = google_classroom.get_classes(uid)
    Courses.objects.filter(owner_id=uid).delete()
    for course in courses:
        new_course = Courses()
        # print(course.get("id"))
        new_course.course_id = course.get("id")
        new_course.name = course.get("name")
        new_course.description = ""  # course.get("description")
        new_course.owner_id = course.get("ownerId")
        new_course.save()
    return render(request, "courses.html", {"courses": courses})

def create_assignment(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    courses = Courses.objects.filter(owner_id=uid).order_by("name")
    return render(request, "create_assignment.html", {"courses": courses})

def save_assignment(request):
    title = request.POST["title"]
    # course_id = request.POST["course"]
    description = request.POST["description"]
    originality_enabled = request.POST["originality_enabled"]
    uid = SocialAccount.objects.filter(user=request.user)[0].uid

    # Save new assignment to database
    assignment = Assignments()
    assignment.title = title
    assignment.course_id = 1
    assignment.description = description
    assignment.originality_check = originality_enabled
    assignment.processed = False
    assignment.owner_id = uid
    print(description)
    if assignment.save() is None:
        messages.add_message(request, messages.SUCCESS, "Assignment created successfully, it will be processed soon!",
                             "alert alert-success fw-bold")
        create_assignment_in_background(assignment.id)
    else:
        messages.add_message(request, messages.ERROR, "Assignment could not be created", "alert alert-danger fw-bold")

    return render(request, "create_assignment.html")

def show_assignments(request, course_id):
    assignments = google_classroom.classroom_get_course_work(course_id)
    print(assignments)
    course = google_classroom.classroom_get_course(course_id)
    return render(request, "assignments_for_course.html", {"course": course, "assignments": assignments})

def create_assignment_in_background(id):
    assignment = get_object_or_404(Assignments, id=id)

    try:
        service = google.get_google_service_instance()
        coursework = {
            'title': assignment.title,
            'description': assignment.description,
            'materials': [
                {'link': {'url': 'http://example.com/ant-colonies'}},
                {'link': {'url': 'http://example.com/ant-quiz'}}
            ],
            'workType': 'ASSIGNMENT',
            'state': 'PUBLISHED',
        }
        coursework = service.courses().courseWork().create(courseId=assignment.course_id, body=coursework).execute()
        print(f"Assignment created with ID {coursework.get('id')}")
        # messages.add_message(request, messages.INFO, "Hello world.", "alert alert-danger fw-bold")
        return HttpResponse(coursework)

    except HttpError as error:
        print('An error occurred: %s' % error)
