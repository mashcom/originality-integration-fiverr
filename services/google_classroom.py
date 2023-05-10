from __future__ import print_function

import mimetypes

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from services import originality
from authentication import google

'''
Get details about a course
'''

def classroom_get_course(course_id, uid):
    try:
        service = google.get_google_service_instance(uid=uid)
        course = service.courses().get(id=course_id).execute()
        print(f"Course found : {course.get('name')}")
        return course
    except HttpError as error:
        print(f"An error occurred: {error}")
        print(course_id)
        return error
    return None

'''Get all assignments for a course'''

def classroom_get_course_work(course_id, uid):
    try:
        service = google.get_google_service_instance(uid)
        results = service.courses().courseWork().list(courseId=course_id).execute()
        if results:
            course_works = results['courseWork']
        else:
            course_works = None
        return course_works
    except Exception as error:
        return error
    return None

"""
Get a list of submissions made by a student
"""

def get_student_submissions(course_id, course_work_id, user_id):
    try:
        service = google.get_google_service_instance(user_id)
        results = service.courses().courseWork().studentSubmissions().list(
            courseWorkId=course_work_id, courseId=course_id, userId=user_id).execute()
        return results
    except Exception as error:
        return error
    return None

def modify_student_submission(submission_id, course_id, course_work_id, google_drive_file_id, uid):
    try:
        service = google.get_google_service_instance(uid=uid)
        attachments = {
            "addAttachments": [
                {
                    "driveFile": {
                        "id": google_drive_file_id
                    }
                }
            ]
        }
        results = service.courses().courseWork().studentSubmissions().modifyAttachments(courseWorkId=course_work_id,
                                                                                        courseId=course_id,
                                                                                        id=submission_id,
                                                                                        body=attachments).execute()
        return results

    except Exception as error:
        return error
    return None

def turn_in_submission(submission_id, course_id, course_work_id, uid):
    try:
        service = google.get_google_service_instance(uid=uid)
        results = service.courses().courseWork().studentSubmissions().turnIn(
            courseWorkId=course_work_id, courseId=course_id, id=submission_id).execute()
        return True
    except Exception as error:
        return error
    return None

def reclaim_submission(submission_id, course_id, course_work_id, uid):
    try:
        service = google.get_google_service_instance(uid=uid)
        results = service.courses().courseWork().studentSubmissions().reclaim(
            courseWorkId=course_work_id, courseId=course_id, id=submission_id).execute()
        return True
    except Exception as error:
        return error
    return None

'''Get single coursework item of a course'''

def classroom_get_course_work_item(course_id, course_work_id, uid):
    try:
        service = google.get_google_service_instance(uid=uid)
        results = service.courses().courseWork().get(
            id=course_work_id, courseId=course_id).execute()
        return results
    except Exception as error:
        return error
    return None

def create_class(name, owner_id, uid, section="", description_heading="", description="", room=""):
    try:
        service = google.get_google_service_instance(uid=uid)
        course = {
            'name': name,
            'section': section,
            'descriptionHeading': description_heading,
            'description': description,
            'room': room,
            'ownerId': owner_id,
            'courseState': 'ACTIVE'
        }
        course = service.courses().create(body=course).execute()
        return True

    except HttpError as error:
        print(f"An error occurred: {error}")
        return f"An error occurred: {error}"

def get_classes(uid):
    try:
        service = google.get_google_service_instance(uid=uid)
        results = service.courses().list(teacherId=uid, courseStates="ACTIVE").execute()
        courses = results.get('courses', [])
        print(courses)
        return courses
    except Exception as error:
        return error

def upload_file(file_path, file_name, uid):
    service = google.get_google_service_instance(uid=uid, api="drive", version="v3")
    print("File Name:" + file_name)
    print(file_path)

    mime_type = '*/*'
    mt = mimetypes.guess_type(file_path)
    if mt:
        mime_type = mt[0]
    file_metadata = {
        'name': file_name,
        'mimeType': mime_type
    }
    media = MediaFileUpload(file_path,
                            mimetype=mime_type,
                            resumable=True)

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print('File ID: ' + file.get('id'))
    return file.get("id")

def get_user_profile(user_id, uid):
    service = google.get_google_service_instance(uid=uid)
    profile = service.userProfiles().get(userId=user_id).execute()
    return profile

def join_class(course_id, enrollment_code, uid):
    student = {
        'userId': uid
    }
    try:
        service = google.get_google_service_instance(uid=uid)
        student = service.courses().students().create(
            courseId=course_id,
            enrollmentCode=enrollment_code,
            body=student).execute()
        print(
            '''User {%s} was enrolled as a student in
               the course with ID "{%s}"'''
            % (student.get('profile').get('name').get('fullName'),
               course_id))
        return student
    except HttpError as error:
        print(error)
        return error
