# coding: utf-8

from odoo.exceptions import UserError, Warning
import base64
from email import header
import json
import binascii
from collections import OrderedDict
import hashlib
import hmac
import logging
from re import T
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


class OrganizationModel(models.Model):
    _name = "organization.organization"
    _description = "Organization"

    # org_id = fields.Char('Organization Id',  groups='base.group_user')
    name = fields.Char('Organization Name')
    logo = fields.Binary('Logo')
    about = fields.Text(string='About', required=True)
    phone = fields.Char(string="Phone number", default='123')
    bank_information = fields.One2many(
        "organization.bank.inforamtion",
        "bank_id",
        readonly=True,
        help="Bank Information detail.",
    )
    states = fields.Many2one('res.country.state', "Which State do you operate")
    # location = fields.Many2many('location.location',string='Location',required=True, store=True)
    sport_type = fields.Many2many('sport.type', string='Sport Type')
    # note = fields.Text('Note')
    server_token = fields.Char('Server Token', default="123")
    user_id = fields.Many2one('res.users', "User")

    default_home_team = fields.Many2one('team.team', "Default Home Team",)
    default_away_team = fields.Many2one('team.team', "Default Away Team")

    # password = fields.Char(String="Password")

    def toJson(self, token=False):
        return{
            "id": self.id,
            "name": self.name,
            "about": self.about,
            "phone": self.phone,
            "sport_type": [i.toJson() for i in self.sport_type],
            # "location":[i.toJson() for i in self.location],
            "states": {
                "id": self.states.id,
                "name": self.states.name,
                "code": self.states.code,
                "country_id": self.states.country_id.id,
            },
            "default_home_team": self.default_home_team.toJson(isToken=True),
            "default_away_team": self.default_away_team.toJson(isToken=True),
            "user_id": {
                "id": self.user_id.id,
                "email": self.user_id.email
            } if token else False,
            "server_token": self.server_token if token else False
        }


class BankInformation(models.Model):
    _name = "organization.bank.inforamtion"
    _description = 'Organizaion Bank Information'

    bank_id = fields.Many2one('organization.organization', string='organization Reference',
                              help='Relation field', ondelete='cascade', index=True, copy=False)
    account = fields.Char('Account Number',  required=True)
    name = fields.Char('Bank', required=True)
    note = fields.Text('Note')


class SportType(models.Model):
    _name = "sport.type"
    _description = 'Sport Type'

    name = fields.Char('Name', required=True)

    def toJson(self):
        return {
            "id": self.id,
            "name": self.name
        }
