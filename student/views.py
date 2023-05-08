from __future__ import print_function

from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.shortcuts import render, HttpResponse

from authentication import google
from services import google_classroom
from .forms import NameForm
from teacher.models import Assignments
from originality.models import Submission

def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid

    form = NameForm()

    try:

        service = google.get_google_service_instance()

        # Call the Classroom API
        results = service.courses().list(studentId=uid).execute()
        courses = results.get('courses', [])

        if not courses:
            messages.add_message(request, messages.ERROR, 'No active course found!',
                                 "alert alert-danger fw-bold")

        return render(request, "classes.html", {"form": form, "classes": courses})

    except Exception as error:
        messages.add_message(request, messages.ERROR, 'An error occurred: %s' % error,
                             "alert alert-danger fw-bold")
        return render(request, "classes.html", {"form": form, "classes": {}})

def course(request, id):
    try:
        assignments = google_classroom.classroom_get_course_work(id)
        course_details = google_classroom.classroom_get_course(id)
        return render(request, "course.html", {"assignments": assignments, "course_details": course_details})
    except Exception as error:
        messages.add_message(request, messages.ERROR, 'An error occurred: %s' % error,
                             "alert alert-danger fw-bold")
        return render(request, "course.html", {"assignments": {}, "course_details": {}})

def course_assignments(request, course_id, assignment_id):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    course_details = {}
    assignment_details = {}
    all_submissions = {}
    local_assignment_config = Assignments.objects.filter(assignment_id=assignment_id).first()
    submitted_documents = Submission.objects.filter(assignment_code=assignment_id, course_code=course_id,
                                                    student_code=uid).order_by("-id")
    all_submissions = google_classroom.get_student_submissions(course_id, assignment_id, uid)
    submission_id = all_submissions['studentSubmissions'][0].get("id")
    try:
        course_details = google_classroom.classroom_get_course(course_id)
        assignment_details = google_classroom.classroom_get_course_work_item(course_id, assignment_id)

    except Exception as error:
        messages.add_message(request, messages.ERROR, 'An error occurred: %s' % error,
                             "alert alert-danger fw-bold")

    response = {
        "assignment_details": assignment_details,
        "course_details": course_details, "uid": uid,
        "local_assignment_config": local_assignment_config,
        "submissions": submitted_documents,
        "google_submission_id": submission_id
    }
    print(response)
    return render(request, "submit_assignment.html", response)

def turn_in(request):
    if request.method == "POST":
        params = request.POST.dict()
        google_submission_id = params.get("google_submission_id")
        course_id = params.get("course_id")
        course_work_id = params.get("assignment_id")

        try:
            turn_in = google_classroom.turn_in_submission(submission_id=google_submission_id, course_id=course_id,
                                                          course_work_id=course_work_id)
            print(turn_in)
            return HttpResponse(turn_in)
        except Exception as error:
            return HttpResponse(error)

    return HttpResponse("Invalid request method!")
