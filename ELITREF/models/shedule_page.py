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

class OfficalBooks(models.Model):
    _name = "offical.book"
    
    ref_name = fields.Char(string='Referee Name',required=True, store=True)
    event_id = fields.Many2one('event.evnet', 'Events')
    sport_type = fields.Many2many('sport.type',string='Sport Type',required=True, store=True)
    date_of_event = fields.Datetime(string="Date of Event", required=True, store=True)
    picture = fields.Binary(string="Picture")
    team = fields.Many2one('team.team',string='Select Team',required=True, store=True)


    

class ConfigurationModel(models.Model):
    _name = "configuration.model"
    
    name = fields.Char(string='Name',required=True, store=True)
    


   
