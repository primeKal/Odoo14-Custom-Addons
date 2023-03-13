# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from . import membership

ISSUE_STATES = [
    ('draft', 'Draft'),
    ('in_progress', 'Requested'),
    ('hr_approval', 'Hr Approval' ),
    ('manager_approval', 'Manager Approval' ),
    ('rejected', 'Rejected'),
    ('closed', 'Closed')
]

class Complaint(models.Model):
    _name = 'member.complaint'

    issue_subject = fields.Text("Issue Subject")
    issue_body = fields.Html("Issue Body")
    issue_date = fields.Date("Issue Raised Date")
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True)
    issue_status = fields.Selection(ISSUE_STATES,
                              'Status', tracking=True,
                              copy=False, default='draft')