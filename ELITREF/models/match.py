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


class MatchModel(models.Model):
    _name = "match.match"

    # match_id = fields.char(string="Match Id", required=True, store=True)
    name = fields.Char(string='Name', required=True, store=True)
    event_id = fields.Many2one(
        'event.event', string='Select Event', required=True, store=True)
    # location_id = fields.Many2one('location.location',string='Select location',required=True, store=True)
    team_1 = fields.Many2one(
        'team.team', string='Select Team 1', required=True, store=True)
    team_2 = fields.Many2one(
        'team.team', string='Select Team 2', required=True, store=True)
    date_of_event = fields.Datetime(
        string="Date of Event", required=True, store=True)
    sport_type = fields.Many2one(
        'sport.type', string='Sport Type', required=True, store=True)
    # , compute="_compute_time",digits=(12, 2))
    start_date_time = fields.Datetime(string='Start Time')
    # , compute="_compute_time",digits=(12, 2))
    end_date_time = fields.Datetime(string='End Time')
    state = fields.Selection([('ready', 'Ready'), ('start', 'Start'), ('end', 'End')], default='ready',
                             string="Status", tracking=True)
    referees = fields.Many2many(
        'referees.referees', string='Referees', store=True)
    # schedule_id = fields.One2many(
    #     "posted.event.shedule",
    #     "ref_id",
    #     readonly=True,
    #     help="event sheduling",
    # )

    # rules = fields.Many2many(
    #     "event.rule.type",
    #     readonly=True,
    #     help="event rules")
    uniform = fields.Selection([('pants', 'Pants'), ('shorts', 'Shorts')], default='pants',
                               string="Uniform Preference", tracking=True)
    # vet = fields.Selection([('vet', 'Vet'),('autoaccept', 'Autoaccept')], default='vet',
    #                          string="Vet", tracking=True)

    # coach_id = fields.Many2one('coach.coach',string='Coach',required=True, store=True)
    seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                      default=lambda self: _('New'))

    def toJson(self, detail=False, match_detail=False):
        if match_detail:
            return{
                "id": self.id,
                "name": self.name,
                "event_id": self.event_id.toJson(detail=True),
                # "location_id":[i.toJson() for i in self.location_id],
                "team_1": self.team_1.toJson(),
                "team_2": self.team_2.toJson(),
                "date_of_event": self.date_of_event,
                "sport_type": self.sport_type.toJson(),
                "start_date_time": self.start_date_time,
                "end_date_time": self.end_date_time,
                "state": self.state,
                "referees": [i.toJson() for i in self.referees],
                # "rules":[i.toJson() for i in self.rules],
                "uniform": self.uniform,
                # "vet":self.vet,
            }

        return{
            "id": self.id,
            "name": self.name,
            "event_id": self.event_id.id if not detail else self.event_id.toJson(from_match=detail),
            # "location_id":[i.toJson() for i in self.location_id],
            "team_1": self.team_1.toJson(),
            "team_2": self.team_2.toJson(),
            "date_of_event": self.date_of_event,
            "sport_type": self.sport_type.toJson(),
            "start_date_time": self.start_date_time,
            "end_date_time": self.end_date_time,
            "state": self.state,
            "referees": [i.toJson() for i in self.referees],
            # "rules":[i.toJson() for i in self.rules],
            "uniform": self.uniform,
            # "vet":self.vet,
        }

    def action_start(self):
        self.state = 'start'

    def action_end(self):
        self.state = 'end'

    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code(
                'match.match') or _('New')
        res = super(MatchModel, self).create(vals)
        return res


class MatchRequests(models.Model):
    _name = "match.match.referee.requests"

    referee_id = fields.Many2one(
        'referees.referees', string='Referee', required=True, store=True)
    match_id = fields.Many2one(
        'match.match', string='Match', required=True, store=True)
    status = fields.Boolean(string='Status', default=False)
    is_declined = fields.Boolean(string='Is Declined', default=False)

    def toJson(self):
        return {
            "id": self.id,
            "match_id": {
                "id": self.match_id.id,
                "name": self.match_id.name
            },
            "referee_id": self.referee_id.toJson(),
            "status": self.status,
            "is_declined": self.is_declined
        }

class RefereeRequest(models.Model):
    _name = "organization.match.referee.requests"

    referee_id = fields.Many2one(
        'referees.referees', string='Referee', required=True, store=True)
    match_id = fields.Many2one(
        'match.match', string='Match', required=True, store=True)
    status = fields.Boolean(string='Status', default=False)
    has_accepted = fields.Boolean(string='Has Accepted', default=False)

    def toJson(self):
        return {
            "id": self.id,
            "match_id": {
                "id": self.match_id.id,
                "name": self.match_id.name
            },
            "referee_id": self.referee_id.toJson(),
            "status": self.status,
            "has_accepted": self.is_declined
        }
