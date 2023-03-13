

from __future__ import print_function
import pytz
import datetime
import json
from odoo.modules.module import get_module_resource,get_resource_path

from odoo import http, modules, tools
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.http import request
import logging

from json import dumps
# from datetime import datetime, timedelta, timezone



import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.oauth2.credentials
import google_auth_oauthlib.flow

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


_logger = logging.getLogger(__name__)

def save_cred():
    print('ready to save yo creds')
    _logger.info(
        'S2U-------------Save Credetnials Invoked')
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    _logger.info('S2U-------------reading from token.json to check if it has data')
    json_file_path = get_module_resource('s2u_online_appointment', 'static/', 'token.json')
    # if json_file_path:
    _logger.info('S2U-------------this is token json',json_file_path)
    print(type(json_file_path))
    if not os.path.getsize(json_file_path) == 0:
        _logger.info('S2U-------------found the token file lets check its data')
        creds = Credentials.from_authorized_user_file(json_file_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            _logger.info('S2U-------------found the tokenbut expired so lets refresh it')
            creds.refresh(Request())
        else:
            _logger.info('S2U-------------no active token found lets use the credentials file to request one')
            json_file_path = get_module_resource('s2u_online_appointment', 'static/', 'credentials.json')
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                json_file_path,
                scopes=SCOPES)
            flow.redirect_uri = 'http://localhost:8069'
            authorization_url, state = flow.authorization_url(
                # Enable offline access so that you can refresh an access token without
                # re-prompting the user for permission. Recommended for web server apps.
                access_type='offline',
                # Enable incremental authorization. Recommended as a best practice.
                include_granted_scopes='true')
            # flow = InstalledAppFlow.from_client_secrets_file(
            #     json_file_path, SCOPES)
            # creds = flow.run_local_server(port=0)


        # Save the credentials for the next run
        json_token_file = get_module_resource('s2u_online_appointment', 'static/', 'token.json')
        with open(json_token_file, 'w+', encoding="utf-8") as token:
            token.write(creds.to_json())



def create_meeting(emails,start_time, end_time,subject,descri):
    str_start= start_time.strftime(r'%Y-%m-%d %H:%M:%S')
    str_end = end_time.strftime(r'%Y-%m-%d %H:%M:%S')
    ss = str_start.split(' ')
    final_start_str = f"{ss[0]}T{ss[1]}"
    ss = str_end.split(' ')
    final_end_str = f"{ss[0]}T{ss[1]}"
    emails.append('kalebteshale72@gmail.com')
    email_list = [{'email':x} for x in emails]



    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    json_file_path = get_module_resource('s2u_online_appointment', 'static/', 'token.json')
    # if json_file_path:
    if not os.path.getsize(json_file_path) == 0:
        creds = Credentials.from_authorized_user_file(json_file_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return {
                'htmllink': 'Not Connected',
                'meetLink': 'Not Connected'
            }
    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'conferenceDataVersion': 1,
            'summary': subject,
            'location': 'Virtual Meeating',
            'description': descri,
            'start': {
                'dateTime': final_start_str,
                'timeZone': 'IST',
            },
            'end': {
                'dateTime': final_end_str,
                'timeZone': 'IST',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=2'
            ],
        'sendNotifications': True,
            'attendees': email_list,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
            'conferenceData': {
                'createRequest': {
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    },
                    'requestId': 'JksKJJSK1KJSK'
                }
            }
        }

        event = service.events().insert(calendarId='primary', sendNotifications=True, conferenceDataVersion=1,body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        print(event)
        return {
            'htmllink': event['htmlLink'],
            'meetLink': event['hangoutLink']
        }
    except HttpError as error:
        print('An error occurred: %s' % error)


