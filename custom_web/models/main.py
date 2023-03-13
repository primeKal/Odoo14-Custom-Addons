# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from . import membership


class Partner(models.Model):
    _inherit = 'res.partner'

    member_type = fields.Char(string='Membership Type', tracking=True)
    mentee_state = fields.Selection(selection=[('free', 'New'), ('waiting', 'Waiting For Matching'), ('matched', 'Matched'), ('rejected', 'Rejected')], default='free')

    associate_member = fields.Many2one('res.partner', string='Associate Member',
        help="A member with whom you want to associate your membership."
             "It will consider the membership state of the associated member.")
    member_lines = fields.One2many('membership.membership_line', 'partner', string='Membership')
    free_member = fields.Boolean(string='Free Member',
        help="Select if you want to give free membership.")
    membership_amount = fields.Float(string='Membership Amount', digits=(16, 2),
        help='The price negotiated by the partner')
    membership_state = fields.Selection(membership.STATE, compute='_compute_membership_state',
        string='Current Membership Status', store=True,
        help='It indicates the membership state.\n'
             '-Non Member: A partner who has not applied for any membership.\n'
             '-Cancelled Member: A member who has cancelled his membership.\n'
             '-Old Member: A member whose membership date has expired.\n'
             '-Waiting Member: A member who has applied for the membership and whose invoice is going to be created.\n'
             '-Invoiced Member: A member whose invoice has been created.\n'
             '-Paying member: A member who has paid the membership fee.')
    membership_start = fields.Date(compute='_compute_membership_state',
        string ='Membership Start Date', store=True,
        help="Date from which membership becomes active.")
    membership_stop = fields.Date(compute='_compute_membership_state',
        string ='Membership End Date', store=True,
        help="Date until which membership remains active.")
    membership_cancel = fields.Date(compute='_compute_membership_state',
        string ='Cancel Membership Date', store=True,
        help="Date on which membership has been cancelled")
    # states = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('approve', 'Approved'),
    #     ('done', 'Done'),
    #     ('cancel', 'Canceled'),
    # ], string='Status',
    #     copy=False, index=True, readonly=True, store=True, tracking=True,
    #   )

    
    
    # def action_done(self):
    #     _logger.info("rrrrrrrrrrrrrrrrrr")
    #     _logger.info(self.user_id)
    #     self.state = 'done'

    # def action_approve(self):
    #     _logger.info("ooooooooooooooooooooo")
    #     _logger.info(self.user_id)
    #     self.state = 'approve'