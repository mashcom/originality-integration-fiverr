import requests
from settings_manager.models import Originality, OriginalityLog
import base64
from originality.models import Submission

def readfile(file_path):
    f = open(file_path, 'r')
    if f.mode == 'r':
        contents = f.read()
        return contents
    return False

def submit_document(params, file_request, file_path):
    settings = get_active_settings();
    headers = {"Authorization": settings.get('key')}

    CourseCode = params.get('CourseCode')
    AssignmentCode = params.get('AssignmentCode')
    MoodleAssignPageNo = "mapn"
    StudentCode = params.get('StudentCode')
    GroupMembers = params.get('GroupMembers')
    OwnerId = params.get('ownerId')

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
    api_request = requests.post(settings.get("api_url") + "documents", request_data, headers=headers)
    response = api_request.json()
    print(type(response))
    response["success"] = False
    if api_request.status_code == 200:
        if "Id" in response:
            request_data["success"] = True
            request_data["originality_id"] = response["Id"]
            request_data["owner_id"] = OwnerId
            _save_submission(response["Id"], request_data)
            return request_data
        return False
    else:
        return response["Message"]

def _save_submission(originality_id, data):
    submission = Submission()
    submission.id = originality_id
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

    return submission.save()


'''
Verify a key with Originality API
'''

def _make_verification_request(originality_key, api_url):
    headers = {"Authorization": originality_key}

    try:
        api_request = requests.get(api_url + "/customers/ping", headers=headers)
        response = api_request.json()
        print(type(response))
        print(response['Pong'])
        return response
    except ConnectionError:
        return False
    except Exception:
        return False

'''
Save setting key value pair to database
'''

def _save_setting(name, setting):
    settings = Originality()
    settings.name = name
    settings.setting = setting
    return settings.save()

'''
Get active settings for the Originality Integration
'''

def get_active_settings():
    key = Originality.objects.get(name="key")
    api_url = Originality.objects.get(name="api_url")
    originality_status = Originality.objects.get(name="originality_status")
    ghost_writer_status = Originality.objects.get(name="ghost_writer_status")
    settings = {
        "key": key.setting,
        "api_url": api_url.setting,
        "originality_status": originality_status.setting,
        "ghost_writer_status": ghost_writer_status.setting
    }
    return settings
