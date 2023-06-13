import json
import logging

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from originality.models import Report
from services import originality_service

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
        if not "Authorization" in request.headers:
            return JsonResponse({"Message": "Authorization key not provided!!!"}, status=401)

        received_key = request.headers["Authorization"]
        if received_key != current_key:
            return JsonResponse({"Message": "Wrong or Empty Credentials"}, status=401)

        if not request.POST.get("assignmentID"):
            return JsonResponse({"Message": "assignmentID is missing"}, status=400)

        if not request.POST.get("grade"):
            return JsonResponse({"Message": "grade field is missing"}, status=400)

        if not request.POST.get("content"):
            return JsonResponse({"Message": "content field is missing"}, status=400)

        if not request.POST.get("ghostwriteReport"):
            return JsonResponse({"Message": "ghostwriteReport field is missing"}, status=400)

        if not request.POST.get("userID"):
            return JsonResponse({"Message": "userID is missing"}, status=400)

        if not request.POST.get("docSequence"):
            return JsonResponse({"Message": "docSequence is missing"}, status=400)

        if not request.POST.get("fileName"):
            return JsonResponse({"Message": "fileName is missing"}, status=400)

        # Save the report
        originality_report = Report()
        originality_report.grade = request.POST.get("grade")
        originality_report.file = request.POST.get("content")

        originality_report.user_id = request.POST.get("userID")
        originality_report.assignment_id = request.POST.get("assignmentID")
        originality_report.doc_sequence = request.POST.get("docSequence")
        originality_report.ghostwrite_report = request.POST.get("ghostwriteReport")
        originality_report.file_name = request.POST.get("fileName")

        originality_report.created_at = timezone.now()
        originality_report.updated_at = timezone.now()
        originality_report.save()
        return JsonResponse({"Id": originality_report.id, "Message": "Report transfer successful"}, status=200)

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
