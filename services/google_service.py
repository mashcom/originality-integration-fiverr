from __future__ import print_function

import mimetypes
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from httplib2 import ServerNotFoundError

# List of scopes required to access Google APIs


SCOPES = ['https://www.googleapis.com/auth/classroom.courses',
          'https://www.googleapis.com/auth/classroom.coursework.students',
          'https://www.googleapis.com/auth/classroom.coursework.me',
          'https://www.googleapis.com/auth/classroom.rosters',
          'https://www.googleapis.com/auth/classroom.rosters.readonly',
          'https://www.googleapis.com/auth/classroom.profile.emails',
          'https://www.googleapis.com/auth/classroom.profile.photos',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.appdata',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive.install',
          ]

def get_google_service_instance(uid, api="classroom", version="v1"):
    # uid = SocialAccount.objects.filter(user=request.user)[0].uid
    token_file = "tokens/" + str(uid) + "_token.json"
    token_file = " token.json"

    google_credentials = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        google_credentials = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not google_credentials or not google_credentials.valid:
        if google_credentials and google_credentials.expired and google_credentials.refresh_token:
            google_credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            flow.redirect_uri = "http://127.0.0.1:8000/auth/oauth_callback"

            auth_url, _ = flow.authorization_url(prompt='consent')
            print(auth_url)
            return auth_url
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(google_credentials.to_json())

    try:
        service = build(api, version, credentials=google_credentials)
        return service
    except HttpError as error:
        print('An errors occurred: %s' % error)
        return False

'''
Get details about a course
'''

def classroom_get_course(course_id, uid):
    try:
        service = get_google_service_instance(uid=uid)
        course = service.courses().get(id=course_id).execute()
        return course
    except HttpError as error:
        return error

'''Get all assignments for a course'''

def classroom_get_course_work(course_id, uid):
    try:
        service = get_google_service_instance(uid)
        results = service.courses().courseWork().list(courseId=course_id).execute()
        if results:
            course_works = results['courseWork']
        else:
            course_works = None
        return course_works
    except Exception as error:
        return error

"""
Get a list of submissions made by a student
"""

def get_student_submissions(course_id, course_work_id, user_id):
    try:
        service = get_google_service_instance(user_id)
        results = service.courses().courseWork().studentSubmissions().list(
            courseWorkId=course_work_id, courseId=course_id, userId=user_id).execute()
        return results
    except Exception as error:
        return error

def modify_student_submission(submission_id, course_id, course_work_id, google_drive_file_id, uid):
    try:
        service = get_google_service_instance(uid=uid)
        attachments = {
            "addAttachments": [{
                "driveFile": {"id": google_drive_file_id}
            }]
        }
        return service.courses().courseWork().studentSubmissions().modifyAttachments(courseWorkId=course_work_id,
                                                                                     courseId=course_id,
                                                                                     id=submission_id,
                                                                                     body=attachments).execute()
    except Exception as error:
        return error

def turn_in_submission(submission_id, course_id, course_work_id, uid):
    try:
        service = get_google_service_instance(uid=uid)
        turn_in = service.courses().courseWork().studentSubmissions().turnIn(
            courseWorkId=course_work_id, courseId=course_id, id=submission_id).execute()
        print("turn in")
        print(turn_in)
        return True
    except Exception as error:
        return False

def reclaim_submission(submission_id, course_id, course_work_id, uid):
    try:
        service = get_google_service_instance(uid=uid)
        service.courses().courseWork().studentSubmissions().reclaim(
            courseWorkId=course_work_id, courseId=course_id, id=submission_id).execute()
        return True
    except Exception as error:
        return error

'''Get single coursework item of a course'''

def classroom_get_course_work_item(course_id, course_work_id, uid):
    try:
        service = get_google_service_instance(uid=uid)
        results = service.courses().courseWork().get(
            id=course_work_id, courseId=course_id).execute()
        return results
    except Exception as error:
        return None

def create_class(name, owner_id, uid, section="", description_heading="", description="", room=""):
    try:
        service = get_google_service_instance(uid=uid)
        course = {
            'name': name,
            'section': section,
            'descriptionHeading': description_heading,
            'description': description,
            'room': room,
            'ownerId': owner_id,
            'courseState': 'ACTIVE'
        }
        service.courses().create(body=course).execute()
        return True

    except HttpError:
        return False

def get_teacher_classes(uid):
    try:
        service = get_google_service_instance(uid=uid)
        results = service.courses().list(teacherId=uid, courseStates="ACTIVE").execute()
        courses = results.get('courses', [])
        return courses
    except ServerNotFoundError as error:
        raise error
    except Exception as error:
        raise error

def get_student_classes(uid):
    try:
        service = get_google_service_instance(uid=uid)
        results = service.courses().list(studentId=uid).execute()
        courses = results.get('courses', [])
        return courses
    except Exception as error:
        raise error

def upload_to_google_drive(file_path, file_name, uid):
    service = get_google_service_instance(uid=uid, api="drive", version="v3")

    # handle the mime type correctly
    mime_type = '*/*'
    guess_mime_type = mimetypes.guess_type(file_path)

    if guess_mime_type:
        mime_type = guess_mime_type[0]

    file_metadata = {
        'name': file_name,
        'mimeType': mime_type
    }
    media = MediaFileUpload(file_path,
                            mimetype=mime_type,
                            resumable=True)
    try:
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get("id")
    except Exception:
        return False

def get_user_profile(user_id, uid):
    service = get_google_service_instance(uid=uid)
    profile = service.userProfiles().get(userId=user_id).execute()
    return profile

def join_class(course_id, enrollment_code, uid):
    student = {
        'userId': uid
    }
    try:
        service = get_google_service_instance(uid=uid)
        student = service.courses().students().create(
            courseId=course_id,
            enrollmentCode=enrollment_code,
            body=student).execute()
        return student
    except HttpError as error:
        return error
