# coding: utf-8

from odoo.exceptions import UserError, Warning
from ast import Store
import base64
from email import header
import json
import binascii
from collections import OrderedDict
import hashlib
import hmac
import logging
from sched import scheduler
from unittest import result

# from numpy import require
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


class EvenetModel(models.Model):
    _name = "event.event"

    # event_id = fields.char(string="Evnet Id", required=True, store=True)
    name = fields.Char(string='Name', required=True, store=True)
    pay_per_game = fields.Float('Pay Per Game', required=True)
    sport_type = fields.Many2many(
        'sport.type', string='Sport Type', required=True, store=True)
    level = fields.Selection([('level_1', 'Level1'), ('level_2', 'Level2'),
                              ('level_3', 'Level3'), ('level_4', 'Level4')], default='level_1',
                             string="Level", tracking=True)

    # crow_size = fields.Integer(string='Crow Size',required=True, store=True)
    location = fields.Many2one(
        'location.location', string='Location', required=True, store=True)
    organization_id = fields.Many2one(
        'organization.organization', string='Organization', required=True, store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft',
                             string="Status", tracking=True)
    # date_of_event = fields.Datetime(string="Date of Event", required=True, store=True)
    # start_time = fields.Datetime(string='Start Time')#, compute="_compute_time",digits=(12, 2))
    # end_time = fields.Datetime(string='End Time')#, compute="_compute_time",digits=(12, 2))
    # excepted_court = fields.Integer('Expected Courts,Fields,Rinks')
    # schedule_id = fields.One2many(
    #     "posted.event.shedule",
    #     "ref_id",
    #     readonly=True,
    #     help="event sheduling",
    # )
    # rules = fields.One2many(
    #     "event.rules",
    #     "rule_id",
    #     readonly=True,
    #     help="event rules",
    # )
    emergency_contact = fields.Char("Emergency Contact")
    seq = fields.Char(string='Event', required=True, copy=False, readonly=True,
                      default=lambda self: _('New'))

    age_group = fields.Selection(
        [('teen', 'Teen'), ('young', 'Young'), ('adult', 'Adult')], string="Age Group", default='adult')
    total_expected_game = fields.Integer("Total Expected Game", default=0)
    rules = fields.Many2many(
        "event.rule.type",
        readonly=True,
        help="event rules")
    vet_or_auto_accept = fields.Selection([('vet', 'Vet'), ('autoaccept', 'Autoaccept')], default='vet',
                                          string="Vet", tracking=True)
    expected_game_per_court = fields.Integer('Expected Game Per Court')
    venue = fields.Char(string='Venue')
    venue_address = fields.Char(string='Venue Address')
    field_of_play = fields.Many2many('event.court.numbers', string="Fields")
    crew_size = fields.Integer('Crew Size')
    rotation = fields.Integer('Rotation of Referees')

    def toJson(self, from_match=False, detail=False):
        if from_match:
            return {
                "id": self.id,
                "name": self.name,
                "venue_address": self.venue_address
            }
        return{
            "id": self.id,
            "name": self.name,
            "pay_per_game": self.pay_per_game,
            "sport_type": [i.toJson() for i in self.sport_type],
            "level": self.level,
            "location": self.location.toJson(),
            "organization_id": self.organization_id.toJson(),
            "state": self.state,
            "expected_game_per_court": self.expected_game_per_court,
            "field_of_play": [i.toJson() for i in self.field_of_play],
            "emergency_contact": self.emergency_contact,
            "age_group": self.age_group,
            "total_expected_game": self.total_expected_game,
            "rules": [i.toJson() for i in self.rules],
            "vet_or_auto_accept": self.vet_or_auto_accept,
            "venue": self.venue,
            "venue_address": self.venue_address
        }

    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code(
                'event.event') or _('New')
        res = super(EvenetModel, self).create(vals)
        return res

    def action_post(self):
        self.state = 'posted'


class CourtTypes(models.Model):
    _name = 'event.court.types'

    name = fields.Char(string="Name")

    def toJson(self):
        return{
            "id": self.id,
            "name": self.name
        }


class EventCourtNumbers(models.Model):
    _name = 'event.court.numbers'

    court_type = fields.Many2one('event.court.types', string='Court Type')
    number_of_court = fields.Integer("Number of court")

    # def compute_display_name(self):
    #     ls = []
    #     for i in self.court_type:
    #         ls.append(i.name)
    #     return ls

    # display_name = fields.Char(compute=compute_display_name, store=False)

    def name_get(self):
        res = []
        for rec in self:
            name = f"{rec.court_type.name}: {rec.number_of_court}"
            res.append((rec.id, name))
            # res.append((rec.id, "%s", "%s" % (rec.court_type.name, rec.number_of_court)))
            # if (rec.type == 'other'):
            #     res.append((rec.id, "%s, %s" % (rec.name, rec.firstname or "")))
            # else:
            #     res.append((rec.id, "%s" % rec.name))
        return res

    def toJson(self):
        return {
            "id": self.id,
            "court_type": self.court_type.toJson(),
            "number_of_court": self.number_of_court
        }


class EventShedule(models.Model):
    _name = 'posted.event.shedule'

    ref_id = fields.Many2one('event.event', string='Event Reference',
                             help='Relation field', ondelete='cascade', index=True, copy=False)
    start_date = fields.Datetime(string="start Date")
    end_date = fields.Datetime(string="end Date")
    location = fields.Many2one('location.location', 'Location')


class EventRules(models.Model):
    _name = 'event.rules'

    rule_id = fields.Many2one('event.event', string='Event Reference',
                              help='Relation field', ondelete='cascade', index=True, copy=False)
    name = fields.Char(string="Rule")
    rule_type = fields.Many2one('event.rule.type', string="Rule Type")


class EventRulesTye(models.Model):
    _name = 'event.rule.type'

    name = fields.Char(string="Rule Type", required=True)

    def toJson(self):
        return{
            "id": self.id,
            "name": self.name,

        }
