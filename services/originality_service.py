import base64
import os.path
import magic
import requests
from django.conf import settings

from originality.models import Submission
from services import google_service
from settings_manager.models import Originality, OriginalityLog

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
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

}

def readfile(file_path):
    f = open(file_path, 'r')
    if f.mode == 'r':
        contents = f.read()
        return contents
    return False

'''
Send file to Originality server and Google Classroom
'''
def submit_document(params, file_request, file_path, uid):
    settings = get_active_settings()
    headers = {"Authorization": settings.get('key')}

    CourseCode = params.get('CourseCode')
    AssignmentCode = params.get('AssignmentCode')
    MoodleAssignPageNo = "mapn"
    StudentCode = params.get('StudentCode')
    GroupMembers = params.get('GroupMembers')
    OwnerId = params.get('ownerId')
    google_submission_id = params.get("google_submission_id")
    originality_check = params.get("originality_check")

    # encode upload file to base64 and save the encoded file
    encoded_file_path = file_path + "_base64"
    base64.encode(open(file_path, 'rb'), open(encoded_file_path, 'wb'))
    base64_encode_file = readfile(encoded_file_path)

    request_data = {
        "FileName": file_request.name,
        "SenderIP": "",
        "FacultyCode": "",
        "FacultyName": "",
        "DeptCode": "",
        "DeptName": "",
        "CourseCategory": "",
        "CourseCode": CourseCode,
        "CourseName": "",
        "AssignmentCode": AssignmentCode,
        "MoodleAssignPageNo": MoodleAssignPageNo,
        "StudentCode": StudentCode,
        "LecturerCode": "",
        "GroupMembers": GroupMembers,
        "DocSequence": 1,
        "file": base64_encode_file,
        "GhostWriterCheck": settings.get('ghost_writer_status'),
        "LinkMoodleFile": AssignmentCode,
        "GovStudentIdMD5": ""
    }


    try:
        # Upload file to google drive and also submit to Google Classroom
        drive_file = google_service.upload_to_google_drive(file_path, file_request.name, uid=uid)
        request_data["google_file_id"] = drive_file

        #modify the submission of a student for specific course work
        modification = google_service.modify_student_submission(submission_id=google_submission_id,
                                                                course_id=CourseCode,
                                                                course_work_id=AssignmentCode,
                                                                google_drive_file_id=drive_file,
                                                                uid=uid)
        google_student_submission_id = modification.get('id')
    except Exception as error:
        print("MODIFICATION ERROR!")
        print(error)
        return error

    request_data["google_student_submission_id"] = google_student_submission_id
    request_data["owner_id"] = OwnerId

    # The file details and mime
    file_mime = file_path_mime(file_path)
    print(file_path_mime(file_path))

    # If an assignment is marked that its not supposed to be check for originality or its not allowed then submit only to Google Classroom
    if originality_check != "YES" or file_mime not in ORIGINALITY_ALLOWED_FILE_TYPES:
        _save_submission(0, request_data)
        return request_data

    # make request to Originality Server
    try:
        api_request = requests.post(settings.get("api_url") + "documents", request_data, headers=headers)
        response = api_request.json()

        response["success"] = False

        # The file was successfully submitted to Originality server
        if api_request.status_code == 200:
            if "Id" in response:
                request_data["success"] = True
                request_data["originality_id"] = response["Id"]
                request_data["id"] = response["Id"]
                _save_submission(response["Id"], request_data)
                return request_data
            return False
        else:
            return response["Message"]
    except Exception as error:
        return error

def _save_submission(originality_id, data):
    submission = Submission()
    submission.originality_id = originality_id
    submission.file_name = data["FileName"]
    submission.course_code = data["CourseCode"]
    submission.assignment_code = data["AssignmentCode"]
    submission.moodle_assign_page_no = data["MoodleAssignPageNo"]
    submission.student_code = data["StudentCode"]
    submission.group_members = data["GroupMembers"]
    submission.doc_sequence = data["DocSequence"]
    submission.file = data["file"]
    submission.ghost_writer_check = data["GhostWriterCheck"]
    submission.link_moodle_file = data["AssignmentCode"]
    submission.owner_id = data["owner_id"]
    submission.google_file_id = data["google_file_id"]
    submission.google_classroom_id = data["google_student_submission_id"]
    return submission.save()

'''
Verify a key with Originality API
'''

def make_verification_request(originality_key, api_url):
    headers = {"Authorization": originality_key}
    try:
        api_request = requests.get(api_url + "/customers/ping", headers=headers)
        response = api_request.json()
        return response
    except ConnectionError as error:
        raise error
    except Exception as error:
        raise error

'''
Save setting key value pair to database
'''

def save_setting(name, setting):
    settings = Originality()
    settings.name = name
    settings.setting = setting
    return settings.save()

'''
Log changes to settings attempts
'''
def log(name, setting, message="", success=False):
    log = OriginalityLog()
    log.name = name
    log.setting = setting
    log.response = message
    log.success = success
    return log.save()

'''
Get active settings for the Originality Integration
'''

def get_active_settings():

    try:
        key = Originality.objects.get(name="key")
        api_url = Originality.objects.get(name="api_url")
        originality_status = Originality.objects.get(name="originality_status")
        ghost_writer_status = Originality.objects.get(name="ghost_writer_status")
        google_client_id = Originality.objects.get(name="google_client_id")
        google_client_secret = Originality.objects.get(name="google_client_secret")
        google_project_id = Originality.objects.get(name="google_project_id")
        settings = {
        "key": key.setting,
        "api_url": api_url.setting,
        "originality_status": originality_status.setting,
        "ghost_writer_status": ghost_writer_status.setting,
        "google_client_id":google_client_id.setting,
        "google_client_secret":google_client_secret.setting,
        "google_project_id":google_project_id.setting
         }
        return settings
    except Exception:
        pass



def handle_uploaded_file(upload_file, uuid, folder="uploads/"):
    new_file_name = uuid + "_" + upload_file.name
    try:
        with open(os.path.join(settings.BASE_DIR, folder) + new_file_name, 'wb+') as destination:
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
