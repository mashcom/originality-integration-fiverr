import datetime
import logging
import os.path
import uuid

import services.google_service
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import render, HttpResponse, redirect
from django.utils import timezone
from googleapiclient.errors import HttpError
from originality_project.decorators import check_user_able_to_see_page, google_authentication_required
from services import google_service, originality_service
from services.exceptions import NoGoogleTokenException
from teacher.models import Assignments, Courses, AssignmentMaterials

# Get a logger instance
logger = logging.getLogger(__name__)

@login_required()
@google_authentication_required()
def index(request):
    uid = get_user_google_ui(request)
    Courses.objects.filter(owner_id=uid).delete()
    courses = {}
    try:
        courses = google_service.get_teacher_classes(uid)
        for course in courses:
            cache_course(course)
        return render(request, "courses.html", {"courses": courses})
    except NoGoogleTokenException as error:
        messages.add_message(request, messages.ERROR, error,
                             "alert alert-danger fw-bold")
        return render(request, "google_permission.html", {"email": "", "url": error})
    except Exception as error:
        messages.add_message(request, messages.ERROR, error,
                             "alert alert-danger fw-bold")
        return render(request, "courses.html", {"courses": courses})

def cache_course(course):
    new_course = Courses()
    new_course.course_id = course.get("id")
    new_course.name = course.get("name")
    new_course.description = ""  # course.get("description")
    new_course.owner_id = course.get("ownerId")
    return new_course.save()

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def create_course(request):
    return render(request, "create_course.html")

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def edit_course(request, course_id):
    uid = get_user_google_ui(request)
    try:
        course = google_service.classroom_get_course(course_id=course_id, uid=uid)
        return render(request, "create_course.html", {"course": course})
    except Exception as error:
        pass

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def save_course(request):
    uid = get_user_google_ui(request)
    if request.method == "POST":
        name = request.POST["name"]
        description = request.POST["description"]
        description_heading = request.POST["description_heading"]
        section = request.POST["section"]
        room = request.POST["room"]
        id = request.POST["id"]

        try:
            course = google_service.create_class(name=name, owner_id=uid, uid=uid, section=section,
                                                 description_heading=description_heading, description=description,
                                                 room=room, id=id)
            if course:
                messages.add_message(request, messages.SUCCESS, "Course request successful",
                                     "alert alert-success fw-bold")
                return redirect(request.META.get('HTTP_REFERER'))
            messages.add_message(request, messages.ERROR, course,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))
        except Exception as error:
            messages.add_message(request, messages.ERROR, error,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def create_assignment(request):
    uid = get_user_google_ui(request)
    settings = originality_service.get_active_settings()
    originality_status_setting = settings.get('originality_status')
    originality_status = False
    if originality_status_setting == "True":
        originality_status = True
    courses = Courses.objects.filter(owner_id=uid).order_by("name")
    return render(request, "create_assignment.html", {"courses": courses, "originality_status": originality_status})

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def edit_assignment(request, course_id, assignment_id):
    uid = get_user_google_ui(request)
    settings = originality_service.get_active_settings()
    originality_status_setting = settings.get('originality_status')
    originality_status = False
    if originality_status_setting == "True":
        originality_status = True
    assignment_details = google_service.classroom_get_course_work_item(course_id=course_id,
                                                                       course_work_id=assignment_id, uid=uid)
    course = google_service.classroom_get_course(course_id=course_id, uid=uid)

    local_assignment = Assignments.objects.filter(assignment_id=assignment_id).first()
    due_time = local_assignment.due_time
    courses = Courses.objects.filter(course_id=course_id)
    return render(request, "create_assignment.html",
                  {"courses": courses, "assignment": assignment_details, "originality_status": originality_status,
                   "course": course,
                   "due_time": due_time, "edit_mode": True})

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def show_assignments(request, course_id):
    uid = get_user_google_ui(request)
    try:
        assignments = google_service.classroom_get_course_work(course_id=course_id, uid=uid)
        course = google_service.classroom_get_course(course_id=course_id, uid=uid)
    except Exception as error:
        messages.add_message(request, messages.ERROR, error,
                             "alert alert-success fw-bold")
        return render(request, "assignments_for_course.html", {"course": course, "assignments": assignments})

    # Get the local details of the extracted Google Classroom
    if assignments is not None:
        for assignment in assignments:
            assignment_id = assignment.get("id")
            local_assignment_details = get_assignment_details(assignment_id)
            print(local_assignment_details)
            assignment["originality_check_required"] = False
            assignment["api_created"] = False

            if local_assignment_details is not None:
                assignment["api_created"] = True
                assignment["originality_check_required"] = (local_assignment_details.originality_check == "YES")
            else:
                save_assignment_to_cache(assignment, assignment_id, uid)

    return render(request, "assignments_for_course.html", {"course": course, "assignments": assignments})

def get_assignment_details(assignment_id):
    return Assignments.objects.filter(assignment_id=assignment_id).first()

def get_user_google_ui(request):
    return SocialAccount.objects.filter(user=request.user)[0].uid

def save_assignment_to_cache(assignment, assignment_id, uid):
    description = "No description"
    if assignment.get("description"):
        # The description is empty or evaluates to False
        description = assignment.get("description")

    cache_assignment = Assignments()
    cache_assignment.course_id = assignment.get("courseId")
    cache_assignment.assignment_id = assignment_id
    cache_assignment.owner_id = uid
    cache_assignment.title = assignment.get("title")
    cache_assignment.description = description
    cache_assignment.originality_check = "NO"
    cache_assignment.processed = 1
    return cache_assignment.save()

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def handle_uploaded_file(upload_file, uuid):
    new_file_name = uuid + "_" + upload_file.name
    root_path = os.path.join(settings.BASE_DIR, 'uploads/assignments/')
    os.makedirs(root_path, exist_ok=True)  # Create the directory if it doesn't exist

    # root_path = settings.BASE_DIR, 'uploads/assignments/'
    with open(os.path.join(root_path) + new_file_name, 'wb+') as destination:
        for chunk in upload_file.chunks():
            destination.write(chunk)
    return os.path.join(root_path) + new_file_name

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def toggle_originality(request, assignment_id):
    assignment = get_object_or_404(Assignments, assignment_id=assignment_id)
    uid = get_user_google_ui(request)
    if uid != assignment.owner_id:
        raise PermissionDenied

    new_setting = "NO"
    if assignment.originality_check == "NO":
        new_setting = "YES"
        assignment.resubmission_requested = timezone.now()
    assignment.originality_check = new_setting
    assignment.save()
    messages.add_message(request, messages.ERROR, "Originality status updated successfully",
                         "alert alert-success fw-bold")
    return redirect(request.META.get('HTTP_REFERER'))

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def save_assignment(request):
    if request.method == "POST":
        assignment_id = request.POST["assignment_id"]
        title = request.POST["title"]
        course_id = request.POST["course"]
        description = request.POST["description"]
        originality_enabled = request.POST["originality_enabled"]
        due_date = request.POST["due_date"]
        due_time = request.POST["due_time"]

        uid = get_user_google_ui(request)
        assignment = None
        if assignment_id:
            assignment = Assignments.objects.filter(assignment_id=assignment_id).first()
        if not assignment:
            assignment = Assignments()
        logger.debug("ASSIGNMENT!!")
        logger.debug(assignment)
        assignment.title = title
        assignment.course_id = course_id
        assignment.description = description
        assignment.originality_check = originality_enabled
        assignment.processed = False
        assignment.owner_id = uid
        assignment.due_date = due_date
        assignment.due_time = due_time
        assignment_saved = assignment.save()

        logger.debug("ASSIGNMENT SAVED!!")
        logger.debug(assignment_saved)

        if assignment_saved is None:
            print(assignment)
            files = request.FILES.getlist("files")
            for file in files:
                request_uuid = str(uuid.uuid4())
                uploaded = originality_service.handle_uploaded_file(upload_file=file, uuid=request_uuid,
                                                                    folder="uploads/teacher_assignments/")
                if uploaded != False:
                    google_drive_id = google_service.upload_to_google_drive(file_path=uploaded, file_name=file.name,
                                                                            uid=uid)
                    save_assignment_material(assignment, google_drive_id)

            created = create_assignment_in_background(request, id=assignment.id, uid=uid)
            if created:
                messages.add_message(request, messages.SUCCESS,
                                     "Assignment request successful!",
                                     "alert alert-success fw-bold")
                return redirect("/teacher/assignments/course/" + course_id)

            messages.add_message(request, messages.ERROR, created,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

        else:
            messages.add_message(request, messages.ERROR, "Assignment could not be created",
                                 "alert alert-danger fw-bold")

        return render(request, "create_assignment.html")
    return HttpResponse("Invalid request method")

def save_assignment_material(assignment, google_drive_id):
    assignment_material = AssignmentMaterials()
    assignment_material.assignment_id = assignment.id
    assignment_material.google_drive_id = google_drive_id
    assignment_material.save()

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def create_assignment_in_background(request, id, uid):
    assignment = get_object_or_404(Assignments, id=id)
    due_date = assignment.due_date
    date = datetime.datetime.strptime(due_date, "%m/%d/%Y")
    due_time = assignment.due_time
    due_time_process = datetime.datetime.strptime(due_time, "%H:%M")

    materials = []

    assignment_materials = AssignmentMaterials.objects.filter(assignment_id=assignment.id)
    for material in assignment_materials:
        materials.append({
            "driveFile": {
                "driveFile": {
                    "id": material.google_drive_id
                }
            }
        }, )
    logger.debug("MATERIAL!")
    logger.debug(materials)

    try:
        service = services.google_service.get_google_service_instance(uid=uid)
        coursework_body = {
            'title': assignment.title,
            'description': assignment.description,
            'materials': materials,
            'workType': 'ASSIGNMENT',
            'state': 'PUBLISHED',
            'dueDate': {
                "year": date.year,
                "month": date.month,
                "day": date.day
            },
            "dueTime": {
                "hours": due_time_process.hour,
                "minutes": due_time_process.minute,
            }

        }

        google_assignment_id = assignment.assignment_id
        update_mask = 'title,description,dueDate,dueTime,state'  # Specify the fields to update

        coursework = None
        if google_assignment_id:
            materials = coursework_body.get("materials")
            coursework_body.pop('materials', None)
            coursework = service.courses().courseWork().patch(courseId=assignment.course_id,
                                                              id=google_assignment_id,
                                                              body=coursework_body,
                                                              updateMask=update_mask
                                                              ).execute()

            material_update = service.courses().courseWork().patch(courseId=assignment.course_id,
                                                                   id=google_assignment_id,
                                                                   body={"materials": materials},
                                                                   updateMask='materials',
                                                                   ).execute()
            logger.debug("UPDATED COURSE!")
            logger.debug(material_update)

        if not google_assignment_id:
            coursework = service.courses().courseWork().create(courseId=assignment.course_id,
                                                               body=coursework_body).execute()

        assignment.assignment_id = coursework.get('id')
        assignment.processed = 1
        assignment.save()
        coursework.get("id")
        return True

    except HttpError as error:
        logger.debug('An errors occurred: %s' % error)
        return False

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def delete_assignment(request):
    if request.method == "POST":
        assignment_id = request.POST["assignment_id"]
        course_id = request.POST["course_id"]
        uid = get_user_google_ui(request)
        try:
            google_service.delete_assignment(uid=uid, assignment_id=assignment_id, course_id=course_id)
            assignment = Assignments.objects.get(assignment_id=assignment_id)
            assignment.delete()
            messages.add_message(request, messages.SUCCESS, "Assignment was deleted successfully",
                                 "alert alert-success fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))
        except Exception as error:
            messages.add_message(request, messages.ERROR, error,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

    return HttpResponse("Invalid Request!")

@login_required()
@google_authentication_required()
@check_user_able_to_see_page("teachers")
def delete_course(request):
    if request.method == "POST":
        course_id = request.POST["course_id"]
        uid = get_user_google_ui(request)
        try:
            google_service.delete_course(uid=uid, course_id=course_id)
            course = Courses.objects.get(course_id=course_id)
            course.delete()
            messages.add_message(request, messages.SUCCESS, "Course was deleted successfully",
                                 "alert alert-success fw-bold")
            return redirect('/teacher')
        except Exception as error:
            messages.add_message(request, messages.ERROR, error,
                                 "alert alert-danger fw-bold")
            return redirect(request.META.get('HTTP_REFERER'))

    return HttpResponse("Invalid Request!")