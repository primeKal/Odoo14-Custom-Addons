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


class CourtModel(models.Model):
    _name = "court.court"
    
    # name = fields.Char(string='Name',required=True, store=True)
    # email = fields.Char(string='Email',required=True, store=True)
    # phone = fields.Integer(string='Phone',required=True, store=True)
    # match_id = fields.Many2one('match.match',string='Select Match',required=True, store=True)
    # age = fields.Integer(string='Age',required=True, store=True)
    country = fields.Many2one('res.country',string='Country',required=True, store=True)
    state = fields.Many2one('res.country.state',string='State',required=True, store=True)
    name = fields.Char('Address', required=True)
    # long = fields.Char('Longitude', required=True)
    # lat = fields.Char('Latitude', required=True)

    def toJson(self):
        return{
            "id": self.id,
            "country": {
                "name": self.country.name,
                "currency_id": self.country.currency_id,
                "code": self.country.code,
                "phone_code": self.country.phone_code,
            } ,
             "states": {
                "name": self.state.name,
                "code": self.state.code,
                "country_id": self.state.country_id,
            },
            "name":self.name,
            # "long": self.long,
            # "lat": self.lat
        }

   
