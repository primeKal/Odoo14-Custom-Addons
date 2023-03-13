from odoo import fields, models, api, registry, sql_db
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class ExtendedMrpWorkCenterrrr(models.Model):
    _inherit = 'mrp.routing.workcenter'

    employ_ids = fields.Many2many('hr.employee',string="Memeber(Employee)")
    target = fields.Float('Target')

class MrpIncentive(models.Model):
    _name = 'mrp.incentive'

    name = fields.Char(string='Name')
    state = fields.Selection([
        ('Draft','Draft'),
        ('Approved','Approved')
    ],string='Status', default= 'Draft')
    work_operation = fields.Many2one('mrp.routing.workcenter', string="Manufacturing Operation")

    percent = fields.Integer(string="Percentage Achived", default=1, required=True)

    target = fields.Float(string="Tareget-/Month", required=True)
    paid_amount = fields.Float('Paid Amount', required=True)
    start_date = fields.Datetime(string="Start Time")
    end_date = fields.Datetime(string="End Time", required=True)
    production_count =fields.Integer('Order Count', required=True)
    production_amount =fields.Float('Total Production Qty', required=True)


    def giveIncentive(self):
        print('sdfksdjflksdjflksm,xcvxcm,vnrtiogrehgh[q934ero')
