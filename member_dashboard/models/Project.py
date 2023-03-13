# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from . import membership


class Project(models.Model):
    _inherit = 'project.project'

    #partner_ids = fields.Many2many('res.partner', string='Contributors')