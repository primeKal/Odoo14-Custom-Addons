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


class TeamModel(models.Model):
    _name = "team.team"

    # team_id = fields.Char(string="Team Id", required=True, store=True)
    name = fields.Char(string='Name', required=True, store=True)
    organization_id = fields.Many2one(
        'organization.organization', string='Organization', required=True, store=True)
    crew_size = fields.Integer(string='Crew Size', store=True)
    team_type = fields.Selection([('teamA', 'TeamA'), ('teamB', 'TeamB'),
                                  ('teamc', 'TeamC')], default='teamA',
                                 string="Team Type", tracking=True)
    # event_id = fields.Many2one('event.event',string='Select Event',required=True, store=True)
    sport_type = fields.Many2one('sport.type', 'Sport Type')
    coach_id = fields.Many2one('coach.coach', string='Coach')
    seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                      default=lambda self: _('New'))

    def toJson(self, isToken=False):
        return {
            "id": self.id,
            "name": self.name,
            "organization_id": self.organization_id.toJson() if not isToken else self.organization_id.id,
            "crew_size": self.crew_size,
            "team_type": self.team_type,
            "sport_type": self.sport_type.toJson() if self.sport_type else False,
            "coach_id": self.coach_id.toJson() if self.coach_id else False,

        }

    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code(
                'team.team') or _('New')
        res = super(TeamModel, self).create(vals)
        return res
