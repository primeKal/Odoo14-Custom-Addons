from odoo import fields, models, api, registry, sql_db, _
from odoo.exceptions import UserError

class ProductsDemo(models.TransientModel):
    _name = "products.wiz.sms"
    _description = "A Wizard for productssss"

    product_id = fields.Many2one('product.product', string="product")


class ExtendSale222(models.Model):
    _inherit = 'sale.order'

    def create_wizard(self):
        print('asdfghjklkjhgfdsaswertyui')
        #
        view_id_form = self.env['ir.ui.view'].search([('name', '=', 'product.product.tree')])
        view = view_id_form[0]
        view = view.id
        # action= {}
        # action['type'] = 'ir.actions.act_window'
        # action['name'] = 'name'
        # action['view_type'] = 'form'
        # action['view_mode'] = 'form'
        # action['res_model'] = 'product.product'
        # action['views'] = [(view, 'form')]
        # action['res_id'] = resid
        # action['target'] = 'current'
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'product.product',
            'views': [(False, 'tree')],
            'name': 'Bulk Products',
            'target': 'new',
        }
        # return {
        #     'name': _('test'),
        #     'view_type': 'tree',
        #     'view_mode': 'tree',
        #     'view_id': view,
        #     'res_model': 'product.template',
        #     # 'context': "{'type':'out_invoice'}",
        #     'type': 'ir.actions.act_window',
        #     'target': 'new',
        # }



