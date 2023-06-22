from __future__ import print_function

import os.path
import uuid
from base64 import b64decode
from json import JSONDecodeError

from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.signing import Signer
from django.shortcuts import get_object_or_404
from django.shortcuts import render, HttpResponse, redirect
from django.conf import settings


from originality_project.decorators import check_user_able_to_see_page
from services import google_service, originality_service
from .models import Submission, Report

import logging

# Get a logger instance
logger = logging.getLogger(__name__)

@login_required()
def index(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    submissions = Submission.objects.filter(student_code=uid)
    print(submissions)
    return render(request, "submissions.html", {"submissions": submissions})

@login_required()
def submit_to_originality(request):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    if request.method == "POST":
        params = request.POST.dict()
        agreement_accepted = params.get("agreed")
        originality_check = params.get("originality_check")

        if agreement_accepted is None and originality_check == "YES":
            messages.add_message(request, messages.ERROR, "Please acknowledge submission to plagiarism checker","alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER')+"?agreed=false")

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
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    submissions = Submission.objects.filter(owner_id=uid, assignment_code=assignment_id)
    logger.debug("SUBMISSIONS")
    logger.debug(submissions)
    try:
        assignment_details = google_service.classroom_get_course_work_item(course_id=course_id,
                                                                           course_work_id=assignment_id, uid=uid)
        course_details = google_service.classroom_get_course(course_id=course_id, uid=uid)
    except Exception as error:
        messages.add_message(request, messages.ERROR, "There was an errors connecting to Google APIs",
                             "alert alert-success fw-bold")
        return redirect(request.META.get('HTTP_REFERER'))
    reports = []
    unique_reports_set = set()

    for submission in submissions:
        report_entries = Report.objects.filter(assignment_id=submission.assignment_code)
        logger.debug("REPORT ENTRY")
        logger.debug(report_entries)

        for report in report_entries:
            report.submitted_by = submission.student_code
            report.profile = originality_service.get_user_profile(uid=report.user_id)

            # Check if the report is already in the set
            if report not in unique_reports_set:
                reports.append(report)
                unique_reports_set.add(report)

    return render(request, "report.html",
                  {"reports": reports, "assignment": assignment_details, "course_details": course_details})

@login_required()
@check_user_able_to_see_page("students")
def reports_for_student(request, course_id, assignment_id):
    uid = SocialAccount.objects.filter(user=request.user)[0].uid
    submissions = Submission.objects.filter(student_code=uid, assignment_code=assignment_id)
    logger.debug("STUDENT SUBMISSIONS")
    logger.debug(submissions)
    try:
        assignment_details = google_service.classroom_get_course_work_item(course_id=course_id,
                                                                           course_work_id=assignment_id, uid=uid)
        course_details = google_service.classroom_get_course(course_id=course_id, uid=uid)
    except Exception as error:
        messages.add_message(request, messages.ERROR, "There was an errors connecting to Google APIs",
                             "alert alert-success fw-bold")
        return redirect(request.META.get('HTTP_REFERER'))
    reports = []
    unique_reports_set = set()

    for submission in submissions:
        report_entries = Report.objects.filter(assignment_id=submission.assignment_code,user_id=uid)
        logger.debug("REPORT ENTRY")
        logger.debug(report_entries)

        for report in report_entries:
            report.submitted_by = submission.student_code
            report.profile = originality_service.get_user_profile(uid=report.user_id)

            # Check if the report is already in the set
            if report not in unique_reports_set:
                reports.append(report)
                unique_reports_set.add(report)

    return render(request, "report.html",
                  {"reports": reports, "assignment": assignment_details, "course_details": course_details})

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
        path = os.path.join(settings.BASE_DIR,"reports/" + str(id) + '_' + file_name)
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
