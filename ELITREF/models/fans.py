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


class FansModel(models.Model):
    _name = "fans.fans"

    # autho_token = fields.Char(string="Auth Token", required=True, store=True)
    name = fields.Char(string='Name',required=True, store=True)
    phone = fields.Char(string='Phone',required=True, store=True)
    state = fields.Many2one('res.country.state',string='State',required=True, store=True)
    # team = fields.Many2one('team.team',string='Select Team',required=True, store=True)
    # docs = fields.Binary(string="Document")
    seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    server_token = fields.Char('Server Token', default="123")
    user_id = fields.Many2one('res.users', "User", readonly=True)
    # password = fields.Char(String="Password")

    def toJson(self, token=False):
        return {
            "id":self.id,
            "name":self.name,
            "phone":self.phone,
            "user_id":self.user_id if token else False,
            "server_token": self.server_token if token else False,
            "states": {
                "name": self.country.state.name,
                "code": self.country.state.code,
                "country_id": self.country.state.country_id,
            },
        }

   

    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code('fans.fans') or _('New')
        res = super(FansModel, self).create(vals)
        return res