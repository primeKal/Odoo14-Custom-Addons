from odoo import models, fields, api
from odoo.exceptions import UserError

# from .. import controllers

class CustomModels(models.Model):
    _name = 'custom.models'

    display = fields.Char(string="Display Name")
    name = fields.Many2one(string="Model", comodel_name="ir.model")
    fields = fields.Many2many("ir.model.fields",required=True, domain="[('model_id', '=', name)]")


    @api.model
    def create(self, vals):
        model = self.env['ir.model'].search( [ ('id', '=', vals['name']) ])
        if vals:
            vals['display'] = model.display_name
            return super(CustomModels, self).create(vals)

class GraphSettings(models.TransientModel):
    _name = 'graph.settings'
    _inherit = 'res.config.settings'

    graph_model = fields.Char('Model')
    graph_frequency = fields.Char('Frequency')
    graph_days = fields.Char('Days')
    graph_tool = fields.Char('tool')
    graph_field = fields.Char('field')

    def set_values(self):
        super(GraphSettings, self).set_values()
        self.env['ir.config_parameter'].set_param(
            'graph_api.graph_model', self.graph_model,
            'graph_api.graph_frequency', self.graph_frequency,
            'graph_api.graph_days', self.graph_days,
            'graph_api.graph_tool', self.graph_tool,
            'graph_api.graph_field', self.graph_field)

    def get_values(self):
        res = super(GraphSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            graph_model=params.get_param('rental.send_mail'),
            graph_frequency=params.get_param('graph_api.graph_frequency'),
            graph_days=params.get_param('graph_api.graph_days'),
            graph_tool=params.get_param('graph_api.graph_tool'),
            graph_field=params.get_param('graph_api.graph_field')
        )
        return res



