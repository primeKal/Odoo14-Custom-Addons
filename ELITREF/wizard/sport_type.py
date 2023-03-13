
from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)

class SportType(models.TransientModel):
    _name = "sport.wizard"
    _description = "Register Sport Type"

    name = fields.Char(string='Name',required=True, store=True)

    def action_sport_register(self):
        vals = {
            'name': self.name
            
        }
        sport_register = self.env['sport.type'].create(vals)
        return sport_register
