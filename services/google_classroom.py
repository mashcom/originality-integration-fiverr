from __future__ import print_function
from authentication import google
from googleapiclient.errors import HttpError

'''
Get details about a course
'''

def classroom_get_course(course_id):
    try:
        service = google.get_google_service_instance()
        course = service.courses().get(id=course_id).execute()
        print(f"Course found : {course.get('name')}")
        return course
    except HttpError as error:
        print(f"An error occurred: {error}")
        print(f"Course not found: {course_id}")
        return error
    return None

'''Get all assignments for a course'''

def classroom_get_course_work(course_id):
    try:
        service = google.get_google_service_instance()
        results = service.courses().courseWork().list(courseId=course_id).execute()
        if results:
            course_works = results['courseWork']
        else:
            course_works = None
        return course_works
    except Exception as error:
        return error
    return None

'''Get single coursework item of a course'''

def classroom_get_course_work_item(course_id, course_work_id):
    try:
        service = google.get_google_service_instance()
        results = service.courses().courseWork().get(
            id=course_work_id, courseId=course_id).execute()
        return results
    except Exception as error:
        return error
    return None

def get_classes(uid):
    try:
        service = google.get_google_service_instance()
        results = service.courses().list(teacherId=uid).execute()
        courses = results.get('courses', [])
        print(uid)
        return courses
    except Exception as error:
        return error
