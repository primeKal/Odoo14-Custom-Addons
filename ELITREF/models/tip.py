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


class PersonalTip(models.Model):
    _name = "tip.personal"

    referee_id = fields.Many2one('referee.referee',string='Select Referee',required=True, store=True)
    fan_id = fields.Many2one('fans.fans',string='Fan',required=True, store=True)


    def toJson(self):
        return {
            "referee_id": self.referee_id.toJson(),
            "fan_id": self.fan_id.toJson(),
            
        }
    
class TipModel(models.Model):
    _name = "tip.tip"

    fan_id = fields.Many2one('fans.fans',string='Fan',required=True, store=True)
    match_id = fields.Many2one('match.match',string='Select Match',required=True, store=True)
    

    def toJson(self):
        return {
            "fan_id": self.fan_id.toJson(),
            "match_id": self.match_id.toJson(),
            
        }