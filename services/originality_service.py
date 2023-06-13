import base64
import os.path
import magic
import requests
from django.conf import settings
from json import JSONDecodeError
from originality.models import Submission
from services import google_service
from settings_manager.models import Originality, OriginalityLog
from django.core.signing import Signer
from django.contrib.sites.models import Site
import json
import logging
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User


# Get a logger instance
logger = logging.getLogger(__name__)


# This is a list of file mime types that can be sent to Originality server for similarity evaluation
ORIGINALITY_ALLOWED_FILE_TYPES = {
    "application/pdf",
    "text/html",
    "application/xhtml+xml",
    "text/plain",
    "application/rtf",
    "text/csv",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.oasis.opendocument.presentation",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def readfile(file_path):
    f = open(file_path, "r")
    if f.mode == "r":
        contents = f.read()
        return contents
    return False


"""
Send file to Originality server and Google Classroom
"""


def submit_document(params, file_request, file_path, uid):
    settings = get_active_settings()
    headers = {"Authorization": settings.get("key")}
    originality_check = params.get("originality_check")
    originality_api_url = settings.get("api_url")
    originality_key = settings.get("key")

    # before we begin send request lets check id the server is reachable and settings valid
    if originality_check == "YES":
        originality_connection_working = make_verification_request(
            originality_key=originality_key,
            api_url=originality_api_url,
            return_bool=True,
        )
        if originality_connection_working != True:
            raise Exception("The originality server is not working at the moment!")

    CourseCode = params.get("CourseCode")
    AssignmentCode = params.get("AssignmentCode")
    MoodleAssignPageNo = "mapn"
    StudentCode = params.get("StudentCode")
    GroupMembers = params.get("GroupMembers")
    OwnerId = params.get("ownerId")
    CourseName = params.get("CourseName")
    google_submission_id = params.get("google_submission_id")

    # encode upload file to base64 and save the encoded file
    encoded_file_path = file_path + "_base64"
    base64.encode(open(file_path, "rb"), open(encoded_file_path, "wb"))
    base64_encode_file = readfile(encoded_file_path)

    request_data = {
        "FileName": file_request.name,
        "SenderIP": construct_report_api_uri(),
        "FacultyCode": "",
        "FacultyName": "",
        "DeptCode": "",
        "DeptName": "",
        "CourseCategory": "",
        "CourseCode": CourseCode,
        "CourseName": CourseName,
        "AssignmentCode": AssignmentCode,
        "MoodleAssignPageNo": MoodleAssignPageNo,
        "StudentCode": StudentCode,
        "LecturerCode": OwnerId,
        "GroupMembers": GroupMembers,
        "DocSequence": 1,
        "file": base64_encode_file,
        "GhostWriterCheck": settings.get("ghost_writer_status"),
        "LinkMoodleFile": AssignmentCode,
        "GovStudentIdMD5": "",
    }

    try:
        # Upload file to google drive and also submit to Google Classroom
        drive_file = google_service.upload_to_google_drive(
            file_path, file_request.name, uid=uid
        )
        request_data["google_file_id"] = drive_file
        download_link = generate_external_file_link(
            google_file_id=drive_file, file_name=file_request.name
        )
        request_data["LinkMoodleFile"] = download_link
        # modify the submission of a student for specific course work
        modification = google_service.modify_student_submission(
            submission_id=google_submission_id,
            course_id=CourseCode,
            course_work_id=AssignmentCode,
            google_drive_file_id=drive_file,
            uid=uid,
        )
        logger.debug("MODIFICATION DETAILS!")
        logger.debug(modification)
        google_student_submission_id = modification.get("id")
    except Exception as error:
        logger.debug("MODIFICATION ERROR!")
        logger.debug(error)
        return error

    request_data["google_student_submission_id"] = google_student_submission_id
    request_data["owner_id"] = OwnerId

    # The file details and mime
    file_mime = file_path_mime(file_path)
    logger.debug(file_path_mime(file_path))
    logger.debug("allowed: " + str(file_mime in ORIGINALITY_ALLOWED_FILE_TYPES))
    # If an assignment is marked that its not supposed to be check for originality or its not allowed then submit only to Google Classroom
    if originality_check != "YES" or file_mime not in ORIGINALITY_ALLOWED_FILE_TYPES:
        _save_submission(0, request_data)
        return request_data

    logger.debug("uploading...")
    logger.debug(json.dumps(request_data))
    # make request to Originality Server
    api_request = requests.post(
        settings.get("api_url") + "documents", json=request_data, headers=headers
    )
    logger.debug(api_request)
    try:

        # api_request.raise_for_status()
        response = api_request.json()
        logger.debug(response)

        response["success"] = False

        # The file was successfully submitted to Originality server
        if api_request.status_code == 200:
            if "Id" in response:
                request_data["success"] = True
                request_data["originality_id"] = response["Id"]
                request_data["id"] = response["Id"]
                _save_submission(response["Id"], request_data)
                return True

            logger.debug("UPLOAD FALSE RESPONSE!")
            logger.debug(error)
            return False
        else:
            return response["Message"]
    except requests.exceptions.HTTPError as e:
        raise e
    except Exception as error:
        logger.debug("UPLOAD ERROR!")
        logger.debug(error)
        return error


def _save_submission(originality_id, data):

    submission = Submission()
    submission.originality_id = originality_id
    submission.file_name = data["FileName"]
    submission.sender_ip = data["SenderIP"]
    submission.course_code = data["CourseCode"]
    submission.assignment_code = data["AssignmentCode"]
    submission.moodle_assign_page_no = data["MoodleAssignPageNo"]
    submission.student_code = data["StudentCode"]
    submission.group_members = data["GroupMembers"]
    submission.doc_sequence = data["DocSequence"]
    submission.file = data["file"]
    submission.lecturer_code = data["LecturerCode"]
    submission.ghost_writer_check = data["GhostWriterCheck"]
    submission.link_moodle_file = data["LinkMoodleFile"]
    submission.owner_id = data["owner_id"]
    submission.google_file_id = data["google_file_id"]
    submission.google_classroom_id = data["google_student_submission_id"]
    return submission.save()


def generate_external_file_link(google_file_id, file_name):
    # make url signature to download file in future
    signer = Signer()
    signature = signer.sign(file_name)
    document_signature = signature
    host_url = Site.objects.get_current().domain

    url = (
        host_url
        + "/originality/external/download/submission/"
        + google_file_id
        + "/"
        + document_signature
    )
    logger.debug(url)
    return url


"""
Verify a key with Originality API
"""


def make_verification_request(originality_key, api_url, return_bool=False):
    headers = {"Authorization": originality_key}
    try:
        api_request = requests.get(api_url + "/customers/ping", headers=headers)
        response = api_request.json()
        if return_bool:
            return response["Pong"]
        return response
    except ConnectionError as error:
        raise error
    except Exception as error:
        raise error


"""
Save setting key value pair to database
"""


def save_setting(name, setting):
    Originality.objects.filter(name=name).delete()
    settings = Originality()
    settings.name = name
    settings.setting = setting
    return settings.save()


def setting_defined(name):
    return Originality.objects.filter(name=name).exists()


"""
Log changes to settings attempts
"""


def log(name, setting, message="", success=False):
    log = OriginalityLog()
    log.name = name
    log.setting = setting
    log.response = message
    log.success = success
    return log.save()


"""
Get active settings for the Originality Integration
"""


def get_active_settings():

    try:
        key = Originality.objects.get(name="key")
        api_url = Originality.objects.get(name="api_url")
        originality_status = Originality.objects.get(name="originality_status")
        ghost_writer_status = Originality.objects.get(name="ghost_writer_status")
        settings = {
            "key": key.setting,
            "api_url": api_url.setting,
            "originality_status": originality_status.setting,
            "ghost_writer_status": ghost_writer_status.setting,
        }
        return settings
    except Exception as error:
        pass


"""
Get active settings for the Google Classroom Integration
"""


def get_google_active_settings():

    try:
        google_client_id = Originality.objects.get(name="google_client_id")
        google_client_secret = Originality.objects.get(name="google_client_secret")
        google_project_id = Originality.objects.get(name="google_project_id")
        settings = {
            "google_client_id": google_client_id.setting,
            "google_client_secret": google_client_secret.setting,
            "google_project_id": google_project_id.setting,
        }
        return settings
    except Exception as error:
        pass


def handle_uploaded_file(upload_file, uuid, folder="uploads/"):
    new_file_name = uuid + "_" + upload_file.name
    try:
        with open(
            os.path.join(settings.BASE_DIR, folder) + new_file_name, "wb+"
        ) as destination:
            for chunk in upload_file.chunks():
                destination.write(chunk)
        return os.path.join(settings.BASE_DIR, folder) + new_file_name
    except Exception as error:
        return False


def file_path_mime(file_path):
    mime = magic.from_file(file_path, mime=True)
    return mime


def check_in_memory_mime(in_memory_file):
    mime = magic.from_buffer(in_memory_file.read(), mime=True)
    return mime


def construct_report_api_uri():
    current_site = Site.objects.get_current()
    domain = current_site.domain
    domain = domain.split("://")[-1]
    protocol = "https"  # You can change this to 'http' if needed
    path = "/api/v1/report"

    absolute_uri = f"{protocol}://{domain}{path}"
    return absolute_uri


def get_user_profile(uid):
    try:
        social_account = SocialAccount.objects.get(uid=uid)
        user = User.objects.get(id=social_account.user_id)
        user_data = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return user_data
    except SocialAccount.DoesNotExist:
        # Handle the case when the social account with the given uid does not exist
        pass
    except User.DoesNotExist:
        # Handle the case when the user associated with the social account does not exist
        pass
