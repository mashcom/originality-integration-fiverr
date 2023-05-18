from __future__ import print_function

from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.signing import Signer
from django.shortcuts import render, HttpResponse, redirect
from google.auth.exceptions import TransportError

from originality.models import Submission
from originality_project.decorators import check_user_able_to_see_page, google_authentication_required
from services import google_service
from teacher.models import Assignments
from .forms import NameForm

@login_required
@check_user_able_to_see_page("students")
@google_authentication_required()
def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    form = NameForm()
    try:
        courses = google_service.get_student_classes(uid=uid)
        if not courses:
            messages.add_message(request, messages.ERROR, 'No active course found!',
                                 "alert alert-danger fw-bold")

        return render(request, "classes.html", {"form": form, "classes": courses})

    except TransportError as error:
        messages.add_message(request, messages.ERROR,
                             'There was an issue connecting to remote server, please try again',
                             "alert alert-danger fw-bold")
        return render(request, "classes.html", {"form": form, "classes": {}})
    except Exception:
        messages.add_message(request, messages.ERROR,
                             'There was a general error connecting to remote server, please try again',
                             "alert alert-danger fw-bold")
        return render(request, "classes.html", {"form": form, "classes": {}})

@login_required
@check_user_able_to_see_page("students")
@google_authentication_required()
def course(request, id):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    try:
        assignments = google_service.classroom_get_course_work(course_id=id, uid=uid)
        course_details = google_service.classroom_get_course(course_id=id, uid=uid)
        return render(request, "course.html", {"assignments": assignments, "course_details": course_details})
    except Exception as error:
        messages.add_message(request, messages.ERROR, 'An errors occurred: %s' % error,
                             "alert alert-danger fw-bold")
        return render(request, "course.html", {"assignments": {}, "course_details": {}})

@login_required
@check_user_able_to_see_page("students")
@google_authentication_required()
def course_assignments(request, course_id, assignment_id):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    course_details = {}
    assignment_details = {}
    all_submissions = {}
    local_assignment_config = Assignments.objects.filter(assignment_id=assignment_id).first()
    submitted_documents = Submission.objects.filter(assignment_code=assignment_id, course_code=course_id,
                                                    student_code=uid).order_by("-created_at")

    for document in submitted_documents:
        signer = Signer()
        signature = signer.sign(document.file_name)
        document.signature = signature
        document.originality_submitted = (str(document.originality_id) != "" or str(document.originality_id) != "0")
        document.google_submitted = (str(document.google_file_id) != "" or str(document.google_file_id) != "0")
        document.originality_submitted


    try:
        all_submissions = google_service.get_student_submissions(course_id, assignment_id, uid)
        print(all_submissions)
        submission_id = all_submissions['studentSubmissions'][0].get("id")
        submission_state = all_submissions['studentSubmissions'][0].get("state")
        course_details = google_service.classroom_get_course(course_id=course_id, uid=uid)
        assignment_details = google_service.classroom_get_course_work_item(course_id, assignment_id, uid=uid)
        response = {
            "assignment_details": assignment_details,
            "course_details": course_details, "uid": uid,
            "local_assignment_config": local_assignment_config,
            "submissions": submitted_documents,
            "google_submission_id": submission_id,
            "submission_state": submission_state
        }
        return render(request, "submit_assignment.html", response)
    except Exception as error:
        messages.add_message(request, messages.ERROR, 'An errors occurred: %s' % error,
                             "alert alert-danger fw-bold")
        return render(request, "submit_assignment.html")

@login_required
@check_user_able_to_see_page("students")
@google_authentication_required()
def turn_in(request):
    if request.method == "POST":
        uid = SocialAccount.objects.filter(user=request.user)[0].uid
        params = request.POST.dict()
        google_submission_id = params.get("google_submission_id")
        course_id = params.get("course_id")
        course_work_id = params.get("assignment_id")

        try:
            turn_in_response = google_service.turn_in_submission(submission_id=google_submission_id,
                                                                 course_id=course_id,
                                                                 course_work_id=course_work_id, uid=uid)
            if turn_in_response:
                messages.add_message(request, messages.SUCCESS, 'Assignment turn in successful',
                                     "alert alert-success fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

        except Exception as error:
            messages.add_message(request, messages.ERROR, error,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

    return HttpResponse("Invalid request method!")

@login_required
@check_user_able_to_see_page("students")
@google_authentication_required()
def reclaim_submission(request):
    if request.method == "POST":
        uid = SocialAccount.objects.filter(user=request.user)[0].uid
        params = request.POST.dict()
        google_submission_id = params.get("google_submission_id")
        course_id = params.get("course_id")
        course_work_id = params.get("assignment_id")

        try:
            turn_in_response = google_service.reclaim_submission(submission_id=google_submission_id,
                                                                 course_id=course_id,
                                                                 course_work_id=course_work_id, uid=uid)
            if turn_in_response:
                messages.add_message(request, messages.SUCCESS,
                                     'Assignment reclaimed successfully, you can now modify it ',
                                     "alert alert-success fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

        except Exception as error:
            messages.add_message(request, messages.ERROR, error,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

    return HttpResponse("Invalid request method!")

@login_required
@check_user_able_to_see_page("students")
@google_authentication_required()
def join_class(request):
    if request.method == "POST":
        code = request.POST["code"]
        if code == "":
            messages.add_message(request, messages.ERROR, "Class Code is required",
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))
        # response = google_classroom.join_class()

    return render(request, "join_class.html")
