
from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError, UserError
_logger = logging.getLogger(__name__)

class LocationWizard(models.TransientModel):
    _name = "location.wizard"
    _description = "Register Location"

    country = fields.Many2one('res.country',string='Country',required=True, store=True)
    state = fields.Many2one('res.country.state',string='State',required=True, store=True)
    address = fields.Char('Address', required=True)
    # long = fields.Char('Longitude', required=True)
    # lat = fields.Char('Latitude', required=True)
    
    def action_location_register(self):
        vals = {
            'country': self.country,
            'state': self.state,
            'name': self.address,
            # 'long': self.long,
            # 'lat': self.lat
        }
        location_register = self.env['location.location'].create(vals)
        return location_register
