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


class SportModel(models.Model):
    _name = "sport.sport"
    
    name = fields.Char(string='Name',required=True, store=True)
    
    def toJson(self):
        return {
            "name":self.name,
        }