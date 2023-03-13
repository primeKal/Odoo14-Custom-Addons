# coding: utf-8

import base64
from email import header
import json
import binascii
from collections import OrderedDict
import hashlib
import hmac
import logging
from unittest import result
import werkzeug
import werkzeug.utils
from itertools import chain
from odoo import http, _
import requests
from odoo.http import request
from datetime import datetime, timedelta
from werkzeug import urls
from odoo import _, api, models, fields
import logging
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError,Warning 
from datetime import datetime, timedelta


class EventSchedule(models.Model):
    _name = "event.shedule"
    
    name = fields.Char(string='Name',required=True, store=True)
    match_id = fields.Many2one('match.match', string='Match')
    event_id = fields.Many2one('event.event', string='Event')
    start_date = fields.Datetime(string="start Date")
    end_date = fields.Datetime(string="end Date")
    start_time = fields.Datetime(string="start Time")
    end_time = fields.Datetime(string="end Time")
    event_id = fields.Many2one('court.court', string='Court')
    coach = fields.Many2one('coach.coach', string='Coach')
    location = fields.Many2one('location.location', 'Location')
    