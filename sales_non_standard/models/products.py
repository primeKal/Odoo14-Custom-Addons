from odoo import fields, models, api, registry, sql_db
from odoo.exceptions import UserError


class ExtendProductt(models.Model):
    _inherit = 'product.template'
    products = fields.Selection([
        ('Seal', 'Seal'),
        ('Fabric', 'Fabric'),
        ('Fasha', 'Fasha'),
        ('Foam', 'Foam')
    ], string='I Foam')
    fasha_related = fields.Many2one('product.template', string='Related Fabric', required_if_products='Fabric')

    fasha_related2 = fields.Many2one('product.product', string='Related Fabric', required_if_products='Fabric')


   # fasha_ids = fields.Many2many('product.product', 'fasha_relation','owner','related',string='Fashas', required_if_products='Fabric',
   #                               domain="[('products', '=', 'Fasha')]")


class ExtendProductt2(models.Model):
    _inherit = 'product.product'
    fasha_ids = fields.Many2many('product.product', 'fasha_relation','owner','related',string='Fashas', required_if_products='Fabric',
                                 domain="[('products', '=', 'Fasha')]")


class ExtendMrp(models.Model):
    _inherit = 'mrp.production'


    isNOnStandard = fields.Boolean(string="From Non-standard", default=False)
    length = fields.Integer(string="Length", default=0)
    width = fields.Integer(string="Width", default=0)
    height = fields.Integer(string="Height", default=0)
    description = fields.Char(string="Description")




#
    @api.model
    def create(self, vals):
        try :
            sale_name = vals['origin']
            sale = self.env['sale.order'].search([('name', '=', sale_name)])
            if sale.non_standard:
                vals['isNOnStandard'] = True
                vals['length'] = sale.length
                vals['width'] = sale.width
                vals['height'] = sale.height
                vals['description'] = self.description
            res = super(ExtendMrp, self).create(vals)
        except Exception:
            res = super(ExtendMrp, self).create(vals)
        return res
#
#         type = res.products
#         if type == 'Seal':
#             model = 'non_standard.seal'
#         elif type == 'Fabric':
#             model = 'non_standard.fabric'
#         elif type == 'Foam':
#             model = 'non_standard.value'
#         elif type == 'Fasha':
#             model = 'non_standard.fasha'
#         else:
#             return res
#         dd = self.env[model].create({
#             'unit_price': res.list_price,
#             'name': res.display_name,
#             'product': res.id
#         })
#         return res
#
#     @api.model
#     def write(self, vals):
#         res = super(ExtendProductt2, self).write(vals)
#         return res
#
#     @api.onchange('list_price')
#     def _onchange_valueof_this(self):
#         print('in meeee')
#         type = self.products
#         model = ''
#         if type == 'Seal':
#             model = 'non_standard.seal'
#         elif type == 'Fabric':
#             model = 'non_standard.fabric'
#         elif type == 'Foam':
#             model = 'non_standard.value'
#         elif type == 'Fasha':
#             model = 'non_standard.fasha'
#         if model == '':
#             return
#         else:
#             tem = self.env[model].search([])
#             for x in tem:
#                 print(x.id)
#             model = self.env[model].search([('product', '=', self.id)])
#             model.write(
#                 {
#                     'unit_price': self.list_price
#                 }
#             )



# class ManufacturingExtendNonStandard(models.Model):
#     _inherit = 'product.template'
#
#
#
#     shape = fields.Selection([
#         ('Rectangular', 'Rectangular'),
#         ('Circular', 'Circular'),
#         ('Triangular', 'Triangular')
#     ], 'Shape', default='Rectangular')
#     length = fields.Integer(string="Length", default=1)
#     width = fields.Integer(string="Width", default=1)
#     height = fields.Integer(string="Height", default=1)
#
#
#
#     @api.model
#     def create(self, vals):
#         res = super(ExtendProductt2, self).create(vals)