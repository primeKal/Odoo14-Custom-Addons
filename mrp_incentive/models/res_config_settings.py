# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    _100 = fields.Float(string='Above 100%', default=30,config_parameter='mrp_incentive._100')
    _90 = fields.Float(string='Above 90%', default=30, config_parameter='mrp_incentive._90')
    _80 = fields.Float(string='Above 80%', default=30, config_parameter='mrp_incentive._80')
    _65 = fields.Float(string='Above 65%', default=30, config_parameter='mrp_incentive._65')
    _50 = fields.Float(string='Above 50%', default=30, config_parameter='mrp_incentive._50')
