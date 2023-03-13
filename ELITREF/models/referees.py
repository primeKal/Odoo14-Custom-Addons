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
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError,Warning 
from datetime import datetime, timedelta


class RefereesModel(models.Model):
    _name = "referees.referees"

    # autho_token = fields.Char(string="Auth Token", required=True, store=True)
    name = fields.Char(string='Name',required=True, store=True)
    # email = fields.Char(string='Email',required=True, store=True)
    # password = fields.Char(String="Password")
    phone = fields.Char(string='Phone',required=True, store=True)
    year_of_experience = fields.Integer(string='Year Of Expirence', store=True)
    picture = fields.Binary(string="Picture")
    docs = fields.Binary(string="Document")
    preference_list = fields.Many2many('referees.referees.preferences',string='Preferences', store=True)
    sport = fields.Many2many('sport.type',String="Sport")
    about = fields.Text('About')
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved')], default='draft',
                             string="Status", tracking=True)
    style_of_officiating = fields.Char('Style Of Officating')
    location = fields.Many2one('location.location',string='Location', store=True)
    # court = fields.Many2one('court.court',string='Select Court',required=True, store=True)
    # event_type = fields.Many2one('event.event',string='Event Type',required=True, store=True)
    # team = fields.Many2one('team.team',string='Select Team',required=True, store=True)
    country = fields.Many2one('res.country',string='Country',required=True, store=True)
    states = fields.Many2one('res.country.state',string='State',required=True, store=True)
    address = fields.Char('Address')
    seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    server_token = fields.Char('Server Token', default="123")
    user_id = fields.Many2one('res.users', "User", readonly=True)

    is_radius_set = fields.Boolean(string='Is Radius Set', default=False)
    radius = fields.Float(string='Radius', default=0.0)

    is_minimum_pay_per_game_set = fields.Boolean(string='Is Minimum Pay Per Game Set', default=False)
    minimum_pay_per_game = fields.Float(string='Minimum Pay Per Game', default=0.0)

    is_uniform_requirement_set = fields.Boolean(string='Is Uniform Requirement Set', default=False)
    uniform_requirement = fields.Boolean(string='Uniform Requirement', default=False)

    is_minimum_game_set = fields.Boolean(string='Is Minimum Game Set', default=False)
    minimum_game = fields.Integer(string='Minimum Game', default=0)

    is_age_group_set = fields.Boolean(string="Is Age Group Set", default=False)
    age_group = fields.Selection([('teen', 'Teen'), ('young', 'Young'), ('adult', 'Adult')], string="Age Group", default='adult')

    is_competition_level_set = fields.Boolean(string="Is Competition Level Set", default=False)
    competition_level = fields.Selection([('developmental', 'Developmental'), ('youth', 'Youth'), ('jv', 'JV'), ('varsity', 'Varsity')], string="Competition Level", default='developmental')


    # password = fields.Char(String="Password")
    
    def toJson(self, token=False):
        _logger.info("##################IN REF JSON###########")
        _logger.info(self.location)
        _logger.info(self.location.id)
        _logger.info("##################IN REF JSON###########")
        return{
            "id":self.id,
            "name": self.name,
            "phone": self.phone,
            "year_of_experience": self.year_of_experience,
            "picture":self.picture,
            "preference_list":[i.toJson() for i in self.preference_list],
            "style_of_officiating":self.style_of_officiating,
            "location": self.location.toJson() if self.location else False,
            "sport_type":[i.toJson() for i in self.sport],
            "state":self.state,
            "country": {
                "id":self.country.id,
                "name": self.country.name,
                "currency_id": self.country.currency_id.id,
                "code": self.country.code,
                "phone_code": self.country.phone_code,
            },
             "states": {
                "id":self.states.id,
                "name": self.states.name,
                "code": self.states.code,
                "country_id": self.states.country_id.id,
            },
            "address":self.address,
            "is_radius_set": self.is_radius_set,
            "radius": self.radius,
            "is_minimum_pay_per_game_set": self.is_minimum_pay_per_game_set,
            "minimum_pay_per_game": self.minimum_pay_per_game,
            "is_uniform_requirement_set": self.is_uniform_requirement_set,
            "uniform_requirement": self.uniform_requirement,
            "is_minimum_game_set": self.is_minimum_game_set,
            "minimum_game": self.minimum_game,
            "is_age_group_set": self.is_age_group_set,
            "age_group": self.age_group,
            "is_competition_level_set": self.is_competition_level_set,
            "competition_level": self.competition_level,


            "user_id": self.user_id.id if token else False,
            "server_token":self.server_token if token else False
        }


    def action_approve(self):
        self.state = 'approved'


    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code('referees.referees') or _('New')
        res = super(RefereesModel, self).create(vals)
        return res

class RefereesPreferenceModel(models.Model):
    _name = "referees.referees.preferences"

    preference_type = fields.Many2one('referees.referees.preferences.type',string='Preference Type',required=True, store=True)
    preference_value = fields.Char(string='Preference Value', store=True)


    def toJson(self):
        return{
            "id":self.id,
            "preference_type": self.preference_type.toJson(),
            "preference_value": self.preference_value,
           
        }


class RefereesPreferenceTypeModel(models.Model):
    _name = "referees.referees.preferences.type"

    name = fields.Char(string='Name',required=True, store=True)
    accepted_type = fields.Selection([('char', 'Char'), ('int', 'Int'), ('float', 'Float'), ('empty', 'Empty')], default='char',
                             string="Accepted Types", tracking=True)

    def toJson(self):
        return{
            "id":self.id,
            "name": self.name,
            "accepted_type": self.accepted_type
        }

