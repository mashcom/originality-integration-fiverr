from __future__ import print_function

import json
import logging
import os.path
import uuid
from base64 import b64decode
from json import JSONDecodeError

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.signing import Signer
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, HttpResponse, redirect
from originality_project.decorators import check_user_able_to_see_page
from services import google_service, originality_service
from teacher.models import Assignments, Courses, AssignmentMaterials

from .models import Submission, Report, Grade

# Get a logger instance
logger = logging.getLogger(__name__)

@login_required()
def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    submissions = Submission.objects.filter(student_code=uid)
    print(submissions)
    return render(request, "submissions.html", {"submissions": submissions})

@login_required()
@check_user_able_to_see_page("admins")
def course_list(request):
    search_query = request.GET.get('search')
    courses = None
    if search_query is None:
        courses = Courses.objects.all()
    else:
        courses = Courses.objects.filter(name__icontains=search_query)
    courses_with_assignments = []
    for course in courses:
        assignments_in_course = Assignments.objects.filter(course_id=course.course_id).count()
        course.assignments = assignments_in_course
        if assignments_in_course > 0:
            courses_with_assignments.append(course)
    context = {
        "courses": courses_with_assignments,
        "search_query": search_query
    }
    return render(request, "admin_courses.html", context=context)

@login_required()
@check_user_able_to_see_page("admins")
def course_assignments(request, course_id):
    course = Courses.objects.filter(course_id=course_id).first()
    assignments = Assignments.objects.filter(course_id=course_id)
    context = {
        "course": course,
        "assignments": assignments
    }
    return render(request, "admin_course_assignments.html", context=context)

@login_required()
def submit_to_originality(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    if request.method == "POST":
        params = request.POST.dict()
        agreement_accepted = params.get("agreed")
        originality_check = params.get("originality_check")

        if agreement_accepted is None and originality_check == "YES":
            messages.add_message(request, messages.ERROR, "Please acknowledge submission to plagiarism checker",
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER') + "?agreed=false")

        file = request.FILES["file"]
        request_uuid = str(uuid.uuid4())
        uploaded_file_path = originality_service.handle_uploaded_file(upload_file=file, uuid=request_uuid)
        response = originality_service.submit_document(params, file, uploaded_file_path, uid=uid)
        try:

            if response:
                messages.add_message(request, messages.SUCCESS, "Submission successfully sent ",
                                     "alert alert-success fw-bold")
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                messages.add_message(request, messages.ERROR, response,
                                     "alert alert-danger fw-bold")
                return redirect(request.META.get('HTTP_REFERER'))
        except ConnectionError:
            messages.add_message(request, messages.ERROR, 'Request could not be completed check your connection',
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

        except JSONDecodeError as error:
            messages.add_message(request, messages.ERROR, error,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

        except Exception as error:
            logger.debug("ORIGINALITY SUBMIT")
            logger.debug(error)
            messages.add_message(request, messages.ERROR, error,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

@login_required()
@check_user_able_to_see_page("teachers")
def reports_for_teacher(request, course_id, assignment_id):
    is_admin = False
    if request.user.groups.filter(name="admins").exists():
        is_admin = True
        submissions = Submission.objects.filter(assignment_code=assignment_id).first()
    else:
        uid = SocialAccount.objects.filter(user=request.user)[0].uid
        submissions = Submission.objects.filter(owner_id=uid, assignment_code=assignment_id).first()
    logger.debug("SUBMISSIONS")
    logger.debug(submissions)
    assignment_details = Assignments.objects.filter(assignment_id=assignment_id).first()
    course_details = Courses.objects.filter(course_id=course_id).first()

    reports = []
    unique_reports_set = {}
    student_entries = Report.objects.filter(assignment_id=assignment_id)

    student_entries = student_entries.values_list('user_id', flat=True).distinct()
    for student_id in student_entries:
        student_reports = Report.objects.filter(assignment_id=assignment_id, user_id=student_id).order_by(
            F('created_at').desc())
        social_account = SocialAccount.objects.filter(uid=student_id).first()
        student_profile = User.objects.get(id=social_account.user_id)
        grade = Grade.objects.filter(assignment_id=assignment_id, user_id=student_id).first()
        if grade is None:
            grade = "Not Graded"

        original_submission = []
        for report in student_reports:
            submission = Submission.objects.filter(originality_id=report.report_id).first()
            if submission is not None:
                signer = Signer()
                signature = signer.sign(submission.file_name)
                submission.signature = signature
                report.submission = submission
                original_submission.append(report)

        student_report_details = {
            "profile": student_profile,
            "social_account": social_account,
            "grade": grade,
            "reports": original_submission,
            "last_modified": student_reports.order_by('-created_at').values_list('created_at', flat=True).last()

        }
        reports.append(student_report_details)

    context = {
        "reports": reports,
        "assignment": assignment_details,
        "course_details": course_details,
        "is_admin": is_admin
    }
    return render(request, "report.html", context=context)

@login_required()
@check_user_able_to_see_page("students")
def reports_for_student(request, course_id, assignment_id):
    submissions = Submission.objects.filter(assignment_code=assignment_id)
    logger.debug("STUDENT SUBMISSIONS")
    logger.debug(submissions)
    assignment_details = Assignments.objects.filter(assignment_id=assignment_id).first()
    course_details = Courses.objects.filter(course_id=course_id).first()
    reports = []
    unique_reports_set = set()

    for submission in submissions:
        report_entries = Report.objects.filter(assignment_id=submission.assignment_code)
        logger.debug("REPORT ENTRY")
        logger.debug(report_entries)

        for report in report_entries:
            report.submitted_by = submission.student_code
            social_account = SocialAccount.objects.filter(uid=report.user_id).first()
            profile = User.objects.get(id=social_account.user_id)
            report.profile = profile

            # Check if the report is already in the set
            if report not in unique_reports_set:
                reports.append(report)
                unique_reports_set.add(report)

    return render(request, "report.html",
                  {"reports": reports, "assignment": assignment_details, "course_details": course_details})

@login_required()
@check_user_able_to_see_page("teachers")
def save_grade(request):
    logger.debug("API REQUEST!!")
    logger.info(f"Request Method: {request.method}")
    logger.info(f"Request Path: {request.path}")

    # Log request headers
    logger.info("Request Headers:")
    for header, value in request.headers.items():
        logger.info(f"{header}: {value}")

    # Log request GET parameters
    logger.info("GET Parameters:")
    for key, value in request.GET.items():
        logger.info(f"{key}: {value}")

    # Log request POST data
    logger.info("POST Data:")
    for key, value in request.POST.items():
        logger.info(f"{key}: {value}")

        # Log the request body
    logger.info("Request Body:")
    # logger.info(request.body.decode("utf-8"))

    logger.info("User ID:")
    logger.info(request.body)

    if request.method != 'POST':
        return JsonResponse({"Message": "Invalid HTTP method"}, status=400)

    try:
        params = json.loads(request.body)
    except Exception as error:
        return JsonResponse({"Message": error}, status=400)

    if 'user_id' not in params:
        return JsonResponse({"Message": "user_id is missing"}, status=400)

    if 'assignment_id' not in params:
        return JsonResponse({"Message": "assignment_id is missing"}, status=400)

    if 'grade' not in params:
        return JsonResponse({"Message": "Grade is missing"}, status=400)

    if 'total_possible' not in params:
        return JsonResponse({"Message": "Total possible is missing"}, status=400)

    user_id = params.get("user_id")
    assignment_id = params.get("assignment_id")
    grade = params.get("grade")
    total_possible = params.get("total_possible")

    try:
        grade = int(grade)
        total_possible = int(total_possible)
    except ValueError:
        return JsonResponse({"Message": f"Invalid grade/total_possible value. It must be a valid integer."}, status=400)

    if grade < 0:
        return JsonResponse({"Message": f"Grade should be above 0"}, status=400)

    if total_possible < 0:
        return JsonResponse({"Message": f"Total possible grade should be above 0"}, status=400)

    if grade > total_possible:
        return JsonResponse(
            {"Message": f"Grade {grade} cannot be greater than the total possible grade for {total_possible}"},
            status=400)

    grade_exists = Grade.objects.filter(user_id=user_id, assignment_id=assignment_id).first()
    if grade_exists is None:
        save_grade = Grade()
    else:
        save_grade = grade_exists

    save_grade.user_id = user_id
    save_grade.assignment_id = assignment_id
    save_grade.grade = grade
    save_grade.total_possible = total_possible
    if save_grade.save() is None:
        return JsonResponse({"Message": "Grade saved successfully"}, status=200)

    return JsonResponse({"Message": "Grade could not be saved"}, status=500)

@login_required()
def download_report(request, originality_id):
    report = get_object_or_404(Report, id=originality_id)
    b64 = report.file
    return _download_base64(request, report.id, b64, "report.pdf")

@login_required()
def download_submission(request, id, signature):
    submission = get_object_or_404(Submission, id=id)
    if not file_signature_valid(submission.file_name, signature):
        return HttpResponse("Invalid url")
    b64 = submission.file
    return _download_base64(request, submission.id, b64, submission.file_name)

# @login_required()
def file_signature_valid(file_name, signature):
    try:
        signer = Signer()
        signer.unsign(signature)
        return True
    except Exception:
        return False

def external_download_submission(request, file_id, signature):
    submission = get_object_or_404(Submission, google_file_id=file_id)
    if not file_signature_valid(submission.file_name, signature):
        return HttpResponse("Invalid url")
    b64 = submission.file
    return _download_base64(request, submission.id, b64, submission.file_name)

# @login_required()
def _download_base64(request, id, base64_string, file_name):
    try:
        # Decode the Base64 string, making sure that it contains only valid characters

        bytes = b64decode(base64_string)
        path = os.path.join(settings.BASE_DIR, "reports/" + str(id) + '_' + file_name)
        f = open(path, 'wb')
        f.write(bytes)
        f.close()
        file_path = path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                mime = originality_service.file_path_mime(file_path)
                response = HttpResponse(fh.read(), content_type=mime)
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
    except Exception as error:
        logger.error("DOWNLOAD ERROR")
        logger.error(error)
        return error
