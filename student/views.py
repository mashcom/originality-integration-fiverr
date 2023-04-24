from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .forms import NameForm

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/classroom.courses.readonly']

def index(request):
    form = NameForm()
    courses = {'id': '605461815842', 'name': 'test class', 'section': 'section 1',
               'descriptionHeading': 'test class section 1', 'room': '1', 'ownerId': '103928753050975631866',
               'creationTime': '2023-04-21T07:21:01.464Z', 'updateTime': '2023-04-21T07:21:01.464Z',
               'enrollmentCode': '52sqxit', 'courseState': 'ACTIVE',
               'alternateLink': 'https://classroom.google.com/c/NjA1NDYxODE1ODQy',
               'teacherGroupEmail': 'test_class_section_1_teachers_e8e218e3@classroom.google.com',
               'courseGroupEmail': 'test_class_section_1_c67e93da@classroom.google.com',
               'teacherFolder': {'id': '1xsceRR517Ile4cxkoylSJstFCLjgirLrT5SOv481HqiktqC1wNcJZ6Q56sGSBLCRDM89o1rE',
                                 'title': 'test class section 1',
                                 'alternateLink': 'https://drive.google.com/drive/folders/1xsceRR517Ile4cxkoylSJstFCLjgirLrT5SOv481HqiktqC1wNcJZ6Q56sGSBLCRDM89o1rE'},
               'guardiansEnabled': False, 'calendarId': 'classroom103872124139767105188@group.calendar.google.com',
               'gradebookSettings': {'calculationType': 'TOTAL_POINTS', 'displaySetting': 'HIDE_OVERALL_GRADE'}}
    return render(request, "classes.html", {"form": form, "classes": courses})
    """Shows basic usage of the Classroom API.
        Prints the names of the first 10 courses the user has access to.
        """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('classroom', 'v1', credentials=creds)

        # Call the Classroom API
        results = service.courses().list(pageSize=10).execute()
        courses = results.get('courses', [])

        if not courses:
            print('No courses found.')
            return
        # Prints the names of the first 10 courses.
        print('Courses:')
        for course in courses:
            print(course['name'])

    except HttpError as error:
        print('An error occurred: %s' % error)
    courses = {'id': '605461815842', 'name': 'test class', 'section': 'section 1',
               'descriptionHeading': 'test class section 1', 'room': '1', 'ownerId': '103928753050975631866',
               'creationTime': '2023-04-21T07:21:01.464Z', 'updateTime': '2023-04-21T07:21:01.464Z',
               'enrollmentCode': '52sqxit', 'courseState': 'ACTIVE',
               'alternateLink': 'https://classroom.google.com/c/NjA1NDYxODE1ODQy',
               'teacherGroupEmail': 'test_class_section_1_teachers_e8e218e3@classroom.google.com',
               'courseGroupEmail': 'test_class_section_1_c67e93da@classroom.google.com',
               'teacherFolder': {'id': '1xsceRR517Ile4cxkoylSJstFCLjgirLrT5SOv481HqiktqC1wNcJZ6Q56sGSBLCRDM89o1rE',
                                 'title': 'test class section 1',
                                 'alternateLink': 'https://drive.google.com/drive/folders/1xsceRR517Ile4cxkoylSJstFCLjgirLrT5SOv481HqiktqC1wNcJZ6Q56sGSBLCRDM89o1rE'},
               'guardiansEnabled': False, 'calendarId': 'classroom103872124139767105188@group.calendar.google.com',
               'gradebookSettings': {'calculationType': 'TOTAL_POINTS', 'displaySetting': 'HIDE_OVERALL_GRADE'}}
    return render(request, "classes.html", {"form": form, "classes": courses})

def course(request, id):
    #check if the user is the authetic user
    return render(request, "course.html")

def course_assignments(request, course_id, assignment_id):
    #check if the user is the authetic user
    return render(request, "course_assignments.html")
