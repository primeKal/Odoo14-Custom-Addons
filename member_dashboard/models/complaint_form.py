"""This function will create a complain form"""


from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta,datetime

class ComplaintCategory(models.Model):
  _name="complaint.category"
  _description="These will hold a list of categories for complaints"

  name = fields.Char(required=True)
  seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
  responsible_person = fields.Many2many('res.users', string="Responsible Person")


  @api.model
  def create(self, vals):
      if vals.get('seq', _('New')) == _('New'):
        vals['seq'] = self.env['ir.sequence'].next_by_code('complaint.category') or _('New')
        res = super(ComplaintCategory, self).create(vals)
        return res

class Complaints(models.Model):
  _name="member.complaint"
  _description = 'This will contain the form for member complaint'

  user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
  subject = fields.Char(required=True)
  complaint_category = fields.Many2one('complaint.category', string="Complaint Category")
  victim_id = fields.Many2one('res.partner')
  perpertrators = fields.Many2many('hr.employee')
# sources = fields.Many2many('res.partner')
  circumstances= fields.Text()
  conclusion_report = fields.Text(readonly=True)
  state = fields.Selection(string="Complaint status", selection=[('new', 'New'), ('waiting', 'Waiting For Approval'), ('resolved', 'Resolved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='new')
  handler = fields.Many2many(related='complaint_category.responsible_person', readonly=True)
  duration_of_remedy = fields.Integer(readonly=True)
  date_of_remedy = fields.Date(compute="_compute_date_of_remedy", inverse="_inverse_date_of_remedy", readonly=True)
  company_id = fields.Many2one(related='victim_id.company_id')
  seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    

  @api.depends("user_id")
  def create(self, vals):
      if vals.get('seq', _('New')) == _('New'):
          vals['seq'] = self.env['ir.sequence'].next_by_code('member.complaint') or _('New')
      res = super(Complaints, self).create(vals)
      return res

  def complaint_resolved(self):
      """This function will handle the state change when a resolved button is clicked"""
      today = datetime.today().strftime("%m-%d-%Y")
      if self.conclusion_report and self.date_of_remedy.strftime("%m-%d-%Y") == today:
        self.state = 'resolved'
      else:
        raise UserError(_("Please fill in the conclusion report or set the date of remedy to Today's date."))

  def complaint_rejected(self):
      """This function will handle the state change when rejected button is clicked"""
      today = datetime.today().strftime("%m-%d-%Y")
      if self.conclusion_report and self.date_of_remedy.strftime("%m-%d-%Y") == today:
          self.state = 'rejected'
      else:
          raise UserError(_("Please fill in the conclusion report or set the date of remedy to Today's date."))
  def complaint_waiting(self):
      """This function will handle the state change when a resolved button is clicked"""
      today = datetime.today().strftime("%m-%d-%Y")
      if self.conclusion_report and self.date_of_remedy.strftime("%m-%d-%Y") == today:
        self.state = 'waiting'
      else:
        raise UserError(_("Please fill in the conclusion report or set the date of remedy to Today's date."))


  def _inverse_date_of_remedy(self):
      """This function will calculate the duration of remedy"""
      for record in self:
          if record.date_of_remedy:
              days = (record.date_of_remedy - record.create_date).days
              record.duration_of_remedy = int(days)

  @api.depends('duration_of_remedy', 'create_date')
  def _compute_date_of_remedy(self):
      """This function will calculate the date of remedy"""
      for record in self:
          if record.create_date:
              record.date_of_remedy = record.create_date +  timedelta(days=record.duration_of_remedy)
          else:
              record.date_of_remedy = ''

  @api.model
  def create(self, vals):
 #    group = self.env['res.groups'].search([('name', '=', 'member_group_manager')])
 #    is_true = self.env.user.id in group.users.ids
     print(self.user_id)
     return super(Complaints, self).create(vals)


  def write(self, vals):
    """This function will chanage the state when a handler set duration"""
#    print(vals)
#    print(vals.date_of_remedy)
#    print(vals['duration_of_remedy'])
#    if vals['duration_of_remedy'] > 0:
#      self.state = 'waiting for approval'
    return super(Complaints, self).write(vals)

 
    
  