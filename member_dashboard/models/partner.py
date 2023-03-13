# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from . import membership

import logging
_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

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
    project_contribute = fields.Many2many('project.project', string="Contribute Projects")
    type = fields.Char("Membership Type")
    select_mentee = fields.Many2one('res.partner', 'Selected Mentee')
    member = fields.Char()
    mentee_state = fields.Selection(string="Mentee Status",selection=[('free', 'New'), ('waiting', 'Waiting For Matching'), ('matched', 'Matched'), ('rejected', 'Rejected')], default='free')
    request_state = fields.Selection(string="status", selection=[('new', 'New'), ('waiting', 'Waiting For Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='new')
    approved_acc = fields.Boolean(string='Approved',default=False)
    social_media = fields.Char(string='Social Media Link(Face Book')
    instagram = fields.Char(string="Instagram")
    twitter = fields.Char(string="Twitter")
    linkedin = fields.Char(string="Linkedin")

    def approve(self):
        if(not self.approved_acc):
            self.approved_acc = True
            self.send()
    def decline(self):
        if(self.approved_acc):
            self.approved_acc = False
    def send(self):
        print('sending')
        _logger.info('hellooooooo')
        mail_pool = self.env['mail.mail']
        values={}
        values.update({'subject': 'HAQI Membership Approved'})
        values.update({'email_to': self.email})
        values.update({'body_html': 'Dear applicant, your request to join HAQI has been approved.You can log in and access your dashboard at <a href="haqi.org">HAQI</a>. Thank you for your interest!' })
        values.update({'body': 'Dear applicant, your request to join HAQI has been approved.You can log in and access your dashboard at <a href="haqi.org">HAQI</a>. Thank you for your interest!' })
        # values.update({'res_id': 'obj.id' }) #[optional] here is the record id, where you want to post that email after sending
        # values.update({'model': ''Object Name }) #[optional] here is the object(like 'project.project')  to whose record id you want to post that email after sending
        msg_id = mail_pool.create(values)
        _logger.info(msg_id) 
        if msg_id:
            msg_id.send()
            # mail_pool.send([msg_id])
    
    def request_approved(self):
      """This function will handle the state change when a resolved button is clicked"""
      if self.free_member:
        self.request_state = 'approved'
      
    def request_rejected(self):
        """This function will handle the state change when rejected button is clicked"""
        if self.free_member: 
            self.request_state = 'rejected'
    
    def request_waiting(self):
        """This function will handle the state change when rejected button is clicked"""
        if self.free_member: 
            self.request_state = 'waiting'
        

    @api.depends('member_lines.account_invoice_line',
                 'member_lines.account_invoice_line.move_id.state',
                 'member_lines.account_invoice_line.move_id.payment_state',
                 'member_lines.account_invoice_line.move_id.partner_id',
                 'free_member',
                 'member_lines.date_to', 'member_lines.date_from',
                 'associate_member')
    def _compute_membership_state(self):
        today = fields.Date.today()
        for partner in self:
            state = 'none'

            partner.membership_start = self.env['membership.membership_line'].search([
                ('partner', '=', partner.associate_member.id or partner.id), ('date_cancel','=',False)
            ], limit=1, order='date_from').date_from
            partner.membership_stop = self.env['membership.membership_line'].search([
                ('partner', '=', partner.associate_member.id or partner.id),('date_cancel','=',False)
            ], limit=1, order='date_to desc').date_to
            partner.membership_cancel = self.env['membership.membership_line'].search([
                ('partner', '=', partner.id)
            ], limit=1, order='date_cancel').date_cancel

            if partner.membership_cancel and today > partner.membership_cancel:
                partner.membership_state = 'free' if partner.free_member else 'canceled'
                continue
            if partner.membership_stop and today > partner.membership_stop:
                if partner.free_member:
                    partner.membership_state = 'free'
                    continue
            if partner.associate_member:
                partner.associate_member._compute_membership_state()
                partner.membership_state = partner.associate_member.membership_state
                continue

            line_states = [mline.state for mline in partner.member_lines if \
                           (mline.date_to or date.min) >= today and \
                           (mline.date_from or date.min) <= today and \
                           mline.account_invoice_line.move_id.partner_id == partner]

            if 'paid' in line_states:
                state = 'paid'
            elif 'invoiced' in line_states:
                state = 'invoiced'
            elif 'waiting' in line_states:
                state = 'waiting'
            elif 'canceled' in line_states:
                state = 'canceled'

            if state == 'none':
                for mline in partner.member_lines:
                    # if there is an old invoice paid, set the state to 'old'
                    if ((mline.date_from or date.min) < today and (mline.date_to or date.min) < today and \
                            (mline.date_from or date.min) <= (mline.date_to or date.min) and \
                            mline.account_invoice_id and mline.account_invoice_id.payment_state in ('in_payment', 'paid')):
                        state = 'old'
                        break

            if partner.free_member and state != 'paid':
                state = 'free'
            partner.membership_state = state

    @api.constrains('associate_member')
    def _check_recursion_associate_member(self):
        for partner in self:
            level = 100
            while partner:
                partner = partner.associate_member
                if not level:
                    raise ValidationError(_('You cannot create recursive associated members.'))
                level -= 1

    @api.model
    def _cron_update_membership(self):
        partners = self.search([('membership_state', 'in', ['invoiced', 'paid'])])
        # mark the field to be recomputed, and recompute it
        self.env.add_to_compute(self._fields['membership_state'], partners)

    def create_membership_invoice(self, product, amount):
        """ Create Customer Invoice of Membership for partners.
        """
        invoice_vals_list = []
        for partner in self:
            addr = partner.address_get(['invoice'])
            if partner.free_member:
                raise UserError(_("Partner is a free Member."))
            if not addr.get('invoice', False):
                raise UserError(_("Partner doesn't have an address to make the invoice."))

            invoice_vals_list.append({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_line_ids': [
                    (0, None, {'product_id': product.id, 'quantity': 1, 'price_unit': amount, 'tax_ids': [(6, 0, product.taxes_id.ids)]})
                ]
            })

        return self.env['account.move'].create(invoice_vals_list)
