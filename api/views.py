import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from originality.models import Report
from services import originality_service

'''
This is a simple API to receive similarity reports from Originality
'''

@csrf_exempt
def report(request):
    settings = originality_service.get_active_settings()
    current_key = settings.get("key")
    if request.method == "POST":
        params = json.loads(request.body)
        if not "Authorization" in request.headers:
            return JsonResponse({"Message": "Wrong or Empty Credentials"}, status=401)

        received_key = request.headers["Authorization"]
        if received_key != current_key:
            return JsonResponse({"Message": "Wrong or Empty Credentials"}, status=401)

        if not params.get("OriginalityFileId"):
            return JsonResponse({"Message": "OriginalityFileId is missing"}, status=400)

        if not params.get("Grade"):
            return JsonResponse({"Message": "Grade is missing"}, status=400)

        if not params.get("file"):
            return JsonResponse({"Message": "File is missing"}, status=400)

        # Save the report
        new_report = Report()
        new_report.id = params.get("OriginalityFileId")
        new_report.grade = params.get("Grade")
        new_report.file = params.get("file")
        new_report.save()
        return JsonResponse({"Id": new_report.id, "Message": "Report transfer successful"}, status=200)

    return JsonResponse({"Message": "Bad Request.Invalid request type"}, status=403)
