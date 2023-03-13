# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta,datetime
import logging
_logger = logging.getLogger(__name__)

STATE = [
    ('none', 'Non Member'),
    ('canceled', 'Cancelled Member'),
    ('old', 'Old Member'),
    ('waiting', 'Waiting Member'),
    ('invoiced', 'Invoiced Member'),
    ('free', 'Free Member'),
    ('paid', 'Paid Member'),
]

MAPPING_STATE = [
    ('new', 'New'),
    ('waiting', 'Waiting Member'),
    ('approved', 'Approved'),
    ('canceled', 'Cancelled'),
]

# MENTEE_STATE = [
#     ('waiting', 'Waiting'),
#     ('matched', 'Matched'),
#     ('canceled', 'Cancelled'),
# ]



class MembershipLine(models.Model):
    _name = 'membership.membership_line'
    _rec_name = 'partner'
    _order = 'id desc'
    _description = 'Membership Line'

    partner = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True)
    membership_id = fields.Many2one('product.product', string="Membership", required=True)
    date_from = fields.Date(string='From', readonly=True)
    date_to = fields.Date(string='To', readonly=True)
    date_cancel = fields.Date(string='Cancel date')

    date = fields.Date(string='Join Date',
        help="Date on which member has joined the membership")
    member_price = fields.Float(string='Membership Fee',
        digits='Product Price', required=True,
        help='Amount for the membership')
    account_invoice_line = fields.Many2one('account.move.line', string='Account Invoice line', readonly=True, ondelete='cascade')
    account_invoice_id = fields.Many2one('account.move', related='account_invoice_line.move_id', string='Invoice', readonly=True)
    company_id = fields.Many2one('res.company', related='account_invoice_line.move_id.company_id', string="Company", readonly=True, store=True)
    project_contribute = fields.Many2many('project.project', string="Contribute Projects")
    membership_type = fields.Char("Membership Type")
    state = fields.Selection(STATE, compute='_compute_state', string='Membership Status', store=True,
        help="It indicates the membership status.\n"
             "-Non Member: A member who has not applied for any membership.\n"
             "-Cancelled Member: A member who has cancelled his membership.\n"
             "-Old Member: A member whose membership date has expired.\n"
             "-Waiting Member: A member who has applied for the membership and whose invoice is going to be created.\n"
             "-Invoiced Member: A member whose invoice has been created.\n"
             "-Paid Member: A member who has paid the membership amount.")
    member_complaint_ids = fields.One2many('member.complaint', 'victim_id')

    @api.depends('account_invoice_id.state',
                 'account_invoice_id.amount_residual',
                 'account_invoice_id.payment_state')
    def _compute_state(self):
        """Compute the state lines """
        if not self:
            return

        self._cr.execute('''
            SELECT reversed_entry_id, COUNT(id)
            FROM account_move
            WHERE reversed_entry_id IN %s
            GROUP BY reversed_entry_id
        ''', [tuple(self.mapped('account_invoice_id.id'))])
        reverse_map = dict(self._cr.fetchall())
        for line in self:
            move_state = line.account_invoice_id.state
            payment_state = line.account_invoice_id.payment_state

            line.state = 'none'
            if move_state == 'draft':
                line.state = 'waiting'
            elif move_state == 'posted':
                if payment_state == 'paid':
                    if reverse_map.get(line.account_invoice_id.id):
                        line.state = 'canceled'
                    else:
                        line.state = 'paid'
                elif payment_state == 'in_payment':
                    line.state = 'paid'
                elif payment_state in ('not_paid', 'partial'):
                    line.state = 'invoiced'
            elif move_state == 'cancel':
                line.state = 'canceled'



class MentoreMapping(models.Model):
    _name = 'mentor.mapping'

    mentor_id = fields.Many2one("res.partner","Mentor")
    mentee_id = fields.Many2one("res.partner","Mentee")
    state = fields.Selection(MAPPING_STATE, string='Status', store=True,tracking=True,default='new')
    date_from = fields.Date(string='Request')
    date_approved = fields.Date(string='Date Approved', )
    duration = fields.Many2one('mentor.duration',string='Duration')
    date_canceled = fields.Date(string='Cancel date')
    handler = fields.Many2one("res.users","Handler", )
    conclusion_report = fields.Text(readonly=True)
    seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))


    @api.depends("mapping_approved")
    def create(self, vals):
        _logger.info("########## trying")
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code('mentor.mapping') or _('New')
        res = super(MentoreMapping, self).create(vals)
        return res

    def mapping_approved(self):
      """This function will handle the state change when a resolved button is clicked"""
      today = datetime.today().strftime("%m-%d-%Y")
      if self.conclusion_report:
        mentee= self.env['res.partner'].sudo().search([('id','=',self.mentee_id.id)])
        mentor= self.env['res.partner'].sudo().search([('id','=',self.mentor_id.id)])
        
        _logger.info("############ %s",self.mentee_id.id)
        mentee.write({
            'mentee_state': 'matched'
        })
        mentor.write({
                'mentee_state': 'matched'
            })
        self.state = 'approved'   

       
      else:
        raise UserError(_("Please fill in the conclusion[Approval] report"))

    def mapping_rejected(self):
        """This function will handle the state change when rejected button is clicked"""
        today = datetime.today().strftime("%m-%d-%Y")
        if self.conclusion_report:
            mentee= self.env['res.partner'].sudo().search([('id','=',self.mentee_id.id)])
            mentor= self.env['res.partner'].sudo().search([('id','=',self.mentor_id.id)])
            
            _logger.info("############ %s",self.mentee_id.id)
            mentee.write({
                'mentee_state': 'free'
            })
            mentor.write({
                'mentee_state': 'free'
            })
            self.state = 'canceled'
        else:
            raise UserError(_("Please fill in the conclusion[Rejection] report."))



class Duration(models.Model):
    _name = 'mentor.duration'

    
    name = fields.Char(string='Period', store=True,tracking=True,default='Three Months')
    seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    
    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code('mentor.duration') or _('New')
        res = super(Duration, self).create(vals)
        return res
   

   