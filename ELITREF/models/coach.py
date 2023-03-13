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


class CoachModel(models.Model):
    _name = "coach.coach"

    name = fields.Char(string='Name',required=True)
    phone = fields.Char(string='Phone',required=True, store=True)
    organization = fields.Many2one('organization.organization',string='Organization', store=True)
    
    age_group = fields.Selection([('teen/young', 'Teen/Young'), ('youth', 'Youth'),
                              ('adult', 'Adult')], default='teen',
                             string="Age Group", tracking=True)
    seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    server_token = fields.Char('Server Token', default="123")
    user_id = fields.Many2one('res.users', "User", readonly=True)
    # password = fields.Char(String="Password")

   

    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code('coach.coach') or _('New')
        res = super(CoachModel, self).create(vals)
        return res

    def toJson(self, token=False):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "organization": self.organization.id,
            # "organization": self.organization,
            "age_group":self.age_group,
            "user_id": self.user_id.id if token else False,
            "server_token": self.server_token if token else False
        }
       
   
    