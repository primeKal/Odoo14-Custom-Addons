# -*- coding: utf-8 -*-

from __future__ import print_function
from odoo.addons.s2u_online_appointment.helpers import functions
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import werkzeug

import google_auth_oauthlib.flow

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

# If modifying these scopes, delete the file token.json.
from odoo.exceptions import UserError

SCOPES = ['https://www.googleapis.com/auth/calendar']


_logger = logging.getLogger(__name__)




class AppointmentSlot(models.Model):
    _name = 's2u.appointment.slot'
    _order = 'user_id, day, slot'
    _description = "Appointment Slot"
    
    @api.model
    def _get_week_days(self):
        return [
            ('0', _('Monday')),
            ('1', _('Tuesday')),
            ('2', _('Wednesday')),
            ('3', _('Thursday')),
            ('4', _('Friday')),
            ('5', _('Saturday')),
            ('6', _('Sunday'))
        ]

    user_id = fields.Many2one('res.users', string='User', required=True)
    day = fields.Selection(selection=_get_week_days, default='0', string="Day", required=True)
    slot = fields.Float('Slot', required=True)
    connected = fields.Boolean('Credentials COnncetd', default=False)

    @api.constrains('slot')
    def _slot_validation(self):
        for slot in self:
            if functions.float_to_time(slot.slot) < '00:00' or functions.float_to_time(slot.slot) > '23:59':
                raise ValidationError(_('The slot value must be between 0:00 and 23:59!'))

    def save_cred(self):
        print('ready to save yo creds')
        _logger.info(
            'S2U-------------Save Credetnials Invoked')
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        json_file_path = get_module_resource('s2u_online_appointment', 'static/', 'token.json')
        _logger.info('S2U-------------reading from token.json to check if it has data')
        _logger.info('S2U-------------this is token json')
        # if json_file_path:
        print(os.path.getsize(json_file_path))
        if  os.path.getsize(json_file_path) >= 3:
            _logger.info('S2U-------------found the token file lets check its data')
            creds = Credentials.from_authorized_user_file(json_file_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if creds:
            json_creds = creds.to_json()
        _logger.info('S2U--')

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
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                flow.redirect_uri = base_url +'/returned'
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
            # return werkzeug.utils.redirect(authorization_url)
            return {
                "url": authorization_url,
                "type": "ir.actions.act_url"
            }
        #     json_token_file = get_module_resource('s2u_online_appointment', 'static/', 'token.json')
        #     with open(json_token_file, 'w+', encoding="utf-8") as token:
        #         token.write(creds.to_json())
        #     message_id = self.env['message.wizard'].create({'message': _("Success in Authorization, Dont forget to authorize once in a while.")})
        #     return {
        #         'name': _('Successfull'),
        #         'type': 'ir.actions.act_window',
        #         'view_mode': 'form',
        #         'res_model': 'message.wizard',
        #         # pass the id
        #         'res_id': message_id.id,
        #         'target': 'new'
        #     }
        # else:
        #     print('already authorized')
        #     raise UserError('already authorized')
