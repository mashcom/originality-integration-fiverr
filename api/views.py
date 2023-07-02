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
        try:
            params = json.loads(request.body)
        except Exception as error:
            return JsonResponse({"Message": "Invalid request body provided"}, status=400)


        if not "Authorization" in request.headers:
            return JsonResponse({"Message": "Authorization key not provided!!!"}, status=401)

        received_key = request.headers["Authorization"]
        if received_key != current_key:
            return JsonResponse({"Message": "Wrong or Empty Credentials"}, status=401)

        if not params.get('CourseId'):
            return JsonResponse({"Message": "CourseId is missing"}, status=400)

        if not params.get('AssignmentId'):
            return JsonResponse({"Message": "AssignmentId is missing"}, status=400)

        if not params.get('StudentId'):
            return JsonResponse({"Message": "StudentId is missing"}, status=400)

        if not params.get('SequenceNumber'):
            return JsonResponse({"Message": "SequenceNumber is missing"}, status=400)

        if 'PercentOriginal' not in params:
            return JsonResponse({"Message": "PercentOriginal is missing"}, status=400)

        if not params.get('OriginalityReport'):
            return JsonResponse({"Message": "OriginalityReport is missing"}, status=400)

        if not params.get('IsGhostWriterReport'):
            return JsonResponse({"Message": "IsGhostWriterReport is missing"}, status=400)

        if not params.get('ReportId'):
            return JsonResponse({"Message": "ReportId is missing"}, status=400)

        # Save the report
        originality_report = Report()
        originality_report.grade = params.get("PercentOriginal")
        originality_report.file =params.get("OriginalityReport")

        originality_report.user_id = params.get("StudentId")
        originality_report.assignment_id = params.get("AssignmentId")
        originality_report.doc_sequence = params.get("SequenceNumber")
        originality_report.ghostwrite_report = params.get("IsGhostWriterReport")
        originality_report.report_id = params.get("ReportId")
        assignment_id=params.get("AssignmentId")
        originality_report.file_name = assignment_id+"_file.pdf"#request.POST.get("fileName")
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
