import json

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from originality.models import Report
from services import originality_service
import logging
# Get a logger instance
logger = logging.getLogger(__name__)
def index(request):
    host_url = request.scheme + "://" + request.get_host() + request.get_full_path()
    return JsonResponse({"Message": "The API is active", "Host": host_url}, status=200)

'''
This is a simple API to receive similarity reports from Originality
'''

@csrf_exempt
def report(request):
    _log_request(request)
    settings = originality_service.get_active_settings()
    current_key = settings.get("key")
    if request.method == "POST":
        # params = json.loads(request.body)
        # if not "Authorization" in request.headers:
        #     return JsonResponse({"Message": "Wrong or Empty Credentials!!!"}, status=401)

        received_key = request.POST.get("clientKey")
        if received_key != current_key:
            return JsonResponse({"Message": "Wrong or Empty Credentials"}, status=401)

        if not request.POST.get("assignmentID"):
            return JsonResponse({"Message": "assignmentID is missing"}, status=400)

        if not request.POST.get("grade"):
            return JsonResponse({"Message": "grade field is missing"}, status=400)

        if not request.POST.get("content"):
            return JsonResponse({"Message": "content field is missing"}, status=400)

        # Save the report
        new_report = Report()
        # new_report.id = request.POST.get("assignmentID") # request.POST.get("OriginalityFileId")
        new_report.grade = request.POST.get("grade")
        new_report.file = request.POST.get("content")

        new_report.user_id = request.POST.get("userID")
        new_report.assignment_id = request.POST.get("assignmentID")
        new_report.doc_sequence = request.POST.get("docSequence")
        new_report.ghostwrite_report = request.POST.get("ghostwriteReport")
        new_report.file_name = request.POST.get("fileName")

        new_report.created_at = timezone.now()
        new_report.updated_at = timezone.now()
        new_report.save()
        return JsonResponse({"Id": new_report.id, "Message": "Report transfer successful"}, status=200)

    return JsonResponse({"Message": "Bad Request.Invalid request type"}, status=403)


def _log_request(request):
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
    logger.info(request.body.decode("utf-8"))