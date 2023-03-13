from odoo import fields, models, api, registry, sql_db
from odoo.exceptions import UserError


class NonStandardValue(models.Model):
    _name = "non_standard.value"
    _description = "Is a value to be set"

    name = fields.Char(string='Name')

    unit_price = fields.Integer(string="Price", default=1, required=True)
    description = fields.Char(string="Description")
    product = fields.Many2one("product.product", string="Product")

    @api.onchange('product')
    def _onchange_value(self):
        print(self.product.list_price)
        self.unit_price = self.product.list_price
        self.name = self.product.display_name

class FashaVariance(models.Model):
    _name = "non_standard.fasha.variance"
    _description = "This is Fasha variance"

    size = fields.Selection([
        ('6', '6'),
        ('12', '12'),
        ('16', '16'),
        ('20', '20'),
        ('24', '24'),
        ('28','28')
    ], default='6', string='Size')
    price = fields.Float('Price')
    fasha_id = fields.Many2one('non_standard.fasha')


class NonStandardFasha(models.Model):
    _name = "non_standard.fasha"
    _description = "This is Fasha"

    name = fields.Char('Name')
    size = fields.Selection([
        ('6', '6'),
        ('12', '12'),
        ('16', '16'),
        ('20', '20'),
        ('24', '24')
    ], default='6', string='Size')

    unit_price = fields.Float(string="Price", default=1, required=True)
    description = fields.Char(string="Description")
    product = fields.Many2one("product.product", string="Product")
    variant = fields.One2many( "non_standard.fasha.variance",'fasha_id',string="Size Variant")

    @api.onchange('product')
    def _onchange_value(self):
        print(self.product.list_price)
        self.unit_price = self.product.list_price
        self.name = self.product.display_name


class NonStandardSeal(models.Model):
    _name = "non_standard.seal"
    _description = "This is seal"

    name = fields.Char(string='Name', default = "Name")
    unit_price = fields.Float(string="Unit Price")
    product = fields.Many2one("product.product", string="Product")




class NonStandardValue(models.Model):
    _name = "non_standard.fabric"
    _description = "This is fabric"

    size = fields.Float(string="Size", default=1, required=True)
    description = fields.Char(string="Description")
    name = fields.Char(string='Name', default = "Name")
    unit_price = fields.Float(string="Unit Price")
    product = fields.Many2one("product.product", string="Product")

    @api.onchange('product')
    def _onchange_value(self):
        print(self.product.list_price)
        self.unit_price = self.product.list_price
        self.name = self.product.display_name


class ExtendSale(models.Model):
    _inherit = 'sale.order'
    non_standard = fields.Boolean(string='Non Standard', default=False)
    #
    # foam_type = fields.Selection([
    #     ('Supreme', 'Supreme'),
    #     ('Ultimate', 'Ultimate'),
    # ], 'Foam Type', default='Ultimate')
    value = fields.Many2one("product.product", string="Value", domain="[('products', '=', 'Foam')]")

    shape = fields.Selection([
        ('Rectangular', 'Rectangular'),
        ('Circular', 'Circular'),
        ('Triangular', 'Triangular')
    ], 'Shape', default='Rectangular')
    length = fields.Integer(string="Length", default=1)
    width = fields.Integer(string="Width", default=1)
    height = fields.Integer(string="Height", default=1)


    r_length = fields.Integer(string="R.", default=1)
    r_width = fields.Integer(string="R.", default=1)


    volume_price = fields.Float(string="Volume*Price", )
    volume = fields.Float(string="Volume")
    # image_id = fields.Image(string='Foam Image')

    foam_unit_price = fields.Float(string="Unit Price of Foam")

    fabric = fields.Boolean(string="Fabric", default=False)
    # fabric_type = fields.Selection([
    #     ('Type1', 'Type 1'),
    #     ('Type2', 'Type 2'),
    # ], 'Foam Type', default='Type1', required_if_fabric=True)
    fabric_1 = fields.Many2one("product.product", string="Fabric", domain="[('products', '=', 'Fabric')]")
    fabric_2 = fields.Many2one("product.product", string="Fasha", domain="[('products', '=', 'Fasha')]")
    fabric_unit_price = fields.Float(string="H-Unit Price")
    fabric_unit_price_2 = fields.Float(string="V- Unit Price")

    fabric_size_1 = fields.Float(string='H-Size')
    fabric_size_2 = fields.Float(string='Fasha')

    fabric_total_1 = fields.Float(string='H-Fabric Total')
    fabric_total_2 = fields.Float(string='Fasha Total 2')

    tape_edge = fields.Boolean(string="Tape Edge", default=False)
    tape_edge_qty = fields.Float(string='Qty')
    tape_edge_unit_price = fields.Float(string='Unit Price')
    tape_edge_total = fields.Float(string='Tape Total')

    glue = fields.Boolean(string="Glue", default=False)
    glue_qty = fields.Float(string='Qty')
    glue_unit_price = fields.Float(string='Unit Price')

    glue_double = fields.Boolean(string='Double')
    glu_total = fields.Float(string='Glue Total')

    Seal = fields.Boolean(string="Seal", default=False)
    seal_qty = fields.Float(string='Qty')
    # seal_side = fields.Selection(
    #     [
    #         ('1 Sided', '1 Side'),
    #         ('2 Side', '2 Side'),
    #         ('3 Side', '3 Side'),
    #         ('4 Side', '4 Side')
    #     ], 'Number of Side', default='1 Sided'
    # )
    seal_type= fields.Many2one("product.product", string="Seal", domain="[('products', '=', 'Seal')]")
    seal_unit_price = fields.Float(string='Unit Price')
    seal_total = fields.Float(string='Seal Total')
    description = fields.Char(string='Description')

    parent_product = fields.Many2one("product.product", string="Product")

    packrise = fields.Boolean(string="Packrise", default=False)

    packrise_height = fields.Integer(string="Packrise Height", default=1)

    @api.onchange('value')
    def _onchange_value(self):
        self.foam_unit_price = self.value.lst_price

    @api.onchange('seal_type')
    def _onchange_seal(self):
        self.change_seal_data()

    @api.onchange('Seal')
    def _onchange_seal(self):
        if self.Seal:
            self.seal_qty = self.length / 100
    @api.onchange('tape_edge')
    def _onchange_tape(self):
        self.change_tape_edge_data()

    @api.onchange('glue')
    def _onchange_glue(self):
        self.change_glue_data()

    @api.onchange('fabric')
    def _onchange_fabric(self):
        length_m = int(self.length) / 100
        width_m = int(self.width) / 100
        # self.fabric_size_1 = (length_m * width_m * 2)
        self.fabric_size_1 = (length_m  * 2)
        self.fabric_size_2 = (length_m * 2) + (width_m * 2)

    @api.onchange('fabric_1')
    def _onchange_fabric(self):
        self.change_fabric_data()

    @api.onchange('fabric_2')
    def _onchange_fasha(self):
        self.change_fasha_data()

    def change_tape_edge_data(self):
        if self.tape_edge:
            tape_product = self.env['product.product'].search([('name', '=', 'Tape Edge')])
            if not tape_product:
                self.tape_edge = False
                raise UserError('No Tape edge Product detected,please create a prodct called Tape Edge')
            self.tape_edge_qty = ((self.length / 100 * 2) + (self.width / 100 * 2)) * 2
            self.tape_edge_unit_price = tape_product.list_price
            self.tape_edge_total = self.tape_edge_qty * self.tape_edge_unit_price

    def change_glue_data(self):
        if self.glue:
            glue_product = self.env['product.product'].search([('name', '=', 'Glue')])
            if not glue_product:
                self.glue = False
                raise UserError('No Glue Product detected,please create a prodct called Glue')
            # hear if 1 kg of glue = 1 m3 of foam
            self.glue_qty = float(self.volume) / 1
            self.glue_unit_price = glue_product.list_price
            if self.glue_double:
                self.glu_total = self.glue_qty * self.glue_unit_price * 2
            else:
                self.glu_total = self.glue_qty * self.glue_unit_price

    def change_seal_data(self):
        if self.Seal:
            self.seal_qty = self.length / 100
            self.seal_unit_price = self.seal_type.lst_price
            self.seal_total = self.seal_qty * self.seal_unit_price

    def change_fabric_data(self):
        # self.fabric_2 = self.fabric_1
        length_m = int(self.length) / 100
        width_m = int(self.width) / 100
        height_m = int(self.height) / 100
        # self.fabric_size_2 = (length_m  * 2) + ( width_m * 2)
        self.fabric_size_1 = (length_m  * 2)
        temp = self.find_heigth(self.height)
        name = ''
        fashas = self.fabric_1.fasha_ids

        try :
            print('haloo')
            product_attribut =self.env['product.attribute'].search([('name','=', 'size')])[0]
            product_value = self.env['product.attribute.value'].search([('name', '=', str(temp))])
            attribute_and_value_object = self.env['product.template.attribute.value'].search(
                [('name', '=', product_value.name), ('attribute_id', '=', product_attribut.id)])
            temporary = attribute_and_value_object.ptav_product_variant_ids
            found_product = ''
            for asss in temporary:
                print(asss)
                if asss in fashas:
                    found_product = asss

            if found_product:
                self.fabric_2 = found_product
        except Exception as e:
            print('--------------------------here error occured ---------------------------')
            

        self.fabric_unit_price = self.fabric_1.lst_price
        # self.fabric_unit_price_2 = self.fabric_1.unit_price
        self.fabric_total_1 = self.fabric_size_1 * self.fabric_unit_price
        # self.fabric_total_2 = self.fabric_size_2 * self.fabric_unit_price_2

    def change_fasha_data(self):
        length_m = int(self.length) / 100
        width_m = int(self.width) / 100
        self.fabric_size_2 = (length_m * 2) + (width_m * 2)
        temp = self.find_heigth(self.height)
        self.fabric_unit_price_2 = self.fabric_2.lst_price
        # variants = self.fabric_2.variant
        # flag = False
        # for x in variants:
        #     if int(x.size) == temp:
        #         self.fabric_unit_price_2 = x.price
        #         flag = True
        # if not flag:
        #     self.fabric_unit_price_2 = self.fabric_2.unit_price
        # self.fabric_total_2 = self.fabric_size_2 * self.fabric_unit_price_2

    @api.onchange('length', 'width', 'height',
                  'foam_unit_price','packrise_height',
                  'packrise','seal_type', 'fabric_total_1',
                  'fabric_total_2','seal_total','glu_total','glue_double',
                  'tape_edge_total','Seal','glue', 'tape_edge','fabric')
    def _onchange_dimention(self):
        if not self.non_standard:
            return
        self.r_length = (self.convert_length(self.length/100)*100)
        print('length is from now one=', self.length)
        self.r_width = (self.convert_width(self.width/100)*100)
        print('width is from now one', self.width)
        length_m = self.r_length / 100
        width_m = self.r_width / 100
        temp = self.height
        if self.packrise:
            temp = self.height + self.packrise_height
            height_m = temp / 100
            volume = (length_m * width_m * height_m)/2
            unrounde_volum = ((temp * self.length * self.width) / 1000000)/2
        else:
            height_m = temp / 100
            volume = length_m * width_m * height_m
            print(volume)
            unrounde_volum = (temp * self.length * self.width) / 1000000

        self.volume =unrounde_volum
        self.volume_price = volume * self.foam_unit_price
        # if self.packrise:
        #     self.volume_price = self.volume_price/2
        self.description = str('Calculated Volume(m3):') + str(self.volume) + str('Calculated Price') + str(
            self.volume_price)
        self.change_fabric_data()
        self.change_fasha_data()
        self.change_tape_edge_data()
        self.change_seal_data()
        self.change_glue_data()
        total = self.volume_price
        if (self.fabric):
            print(total)
            print(self.fabric_total_2)
            print(self.fabric_total_1)
            total = float(total) + float(self.fabric_total_2)
            total = float(total) + float(self.fabric_total_1)
        if (self.Seal):
            total = total + self.seal_total
        if (self.tape_edge):
            total = total + self.tape_edge_total
        if self.glue:
            total = total + self.glu_total
        name = str(self.value.display_name)
        if self.fabric:
            name+=str(self.fabric_1.display_name)
        if self.tape_edge:
            name = name + 'TapedEdge'
        name += str(self.length) + '*' + str(self.width) + '*' + str(self.height)
        self.description = name + str('Sub Total') + str(total)

        # self.description = str('Sub Total') + str(total)



    def calculate_and_save(self):
        print("beggining to calculate the total price")
        if not self.parent_product:
            raise UserError('PLease select the parent product')
        total = self.volume_price
        if (self.fabric):
            print(total)
            print(self.fabric_total_2)
            print(self.fabric_total_1)
            total = float(total) + float(self.fabric_total_2)
            total = float(total) + float(self.fabric_total_1)
        if (self.Seal):
            total = total + self.seal_total
        if (self.tape_edge):
            total = total + self.tape_edge_total
        if self.glue:
            total = total + self.glu_total
        try:
            self.create_variant_and_save(total)
        except Exception as e:
            print(e)
            self.create_product_and_add_order_line(total)

    def find_product_add_order_line(self, total, attribute):
        order_lines = self.order_line
        for product in order_lines:
            if product.price_unit == total:
                if product.product_tmpl_id == self.parent_product.product_tmpl_id:
                    product.product_uom_qty += 1

    def create_variant_and_save(self, final_price):
        print('ready todo list')

        product_attribute_lines = self.env['product.template.attribute.line']
        product_attribute = self.env['product.attribute']
        product_attribute_value = self.env['product.attribute.value']
        attribute = product_attribute.search([('name', '=', str('Unique Price'))])
        product = self.env['product.product']
        temp_total = round(final_price, 2)
        order_lines = self.order_line
        # check ifthe product is already in the sale order line
        for product in order_lines:
            if product.price_unit == temp_total:
                if product.product_id.product_tmpl_id.id == self.parent_product.product_tmpl_id.id:
                    product.product_uom_qty += 1
                    return
        # if unique attribue (Unique Price) has not been created lets create is
        if not attribute:
            attribute_vals = {
                'name': str('Unique Price'),
                'create_variant': 'always'
            }
            attribute = product_attribute.create(attribute_vals)
        # find the attribute - value pairing if not create it
        product_value = product_attribute_value.search([('name', '=', str(final_price))])
        if not product_value:
            product_value = product_attribute_value.create({
                'name': final_price,
                'attribute_id': attribute[0].id
            })
        # if current product has this attribute witha avalue just append it if not
        # create and appennd this attriute line
        current_attribute_lines = self.parent_product.attribute_line_ids
        flag = False
        if current_attribute_lines:
            for line in current_attribute_lines:
                if line.display_name == str('Unique Price'):
                    check = line.write({
                        'value_ids': [(4, product_value.id)],
                        # 'attribute_id' : attribute[0].id
                    })

                    flag = True
        if not flag:
            new_aattribute_line = product_attribute_lines.create({
                'product_tmpl_id': self.parent_product.product_tmpl_id.id,
                'attribute_id': attribute[0].id,
                'value_ids': [(6, 0, [product_value.id])]
            })
            # return

        # find the matching product with the following algoruthms and add it to
        # sales order line
        attribute_and_value_object = self.env['product.template.attribute.value'].search(
            [('name', '=', product_value.name), ('attribute_id', '=', attribute[0].id)])
        for x in attribute_and_value_object:
            if x.product_tmpl_id.id == self.parent_product.product_tmpl_id.id:
                att = x
        variant_product = self.env['product.product'].search([('product_template_attribute_value_ids', 'in', att.id)])
        for v in variant_product:
            print(v.product_template_attribute_value_ids)
            print(v.display_name)
        values = {
            # 'list_price': total,
            'price': final_price
        }
        check = variant_product.write(values)
        
        val = {
            "product_id": variant_product.id,
            "product_template_id": variant_product.product_tmpl_id.id,
            "order_id": self.id,
            'name': variant_product.name,
            'price_unit': variant_product.price,
            'product_uom_qty': 1,
            'customer_lead': 30,
            'company_id': self.company_id.id,
            # 'name': self.description
        }
        order_line_object = self.env['sale.order.line'].create(val)
        self.write({'order_line': [(4, order_line_object.id)]})
        order_line_object._onchange_discount()

    def create_product_and_add_order_line(self, final_price):
        product_template = self.env['product.product']
        vals = {
            # "categ_id": self.parent_product.categ_id.id,
            "price": final_price,
            "name": str(
                str(self.shape) + '/' + str(self.height) + '*' + str(self.width) + '*' + str(
                    self.length) + str('(m3)'))
        }
        product_obj = product_template.create(vals)
        val = {
            "product_id": product_obj.id,
            "product_template_id": product_obj.product_tmpl_id.id,
            "order_id": self.id,
            'name': product_obj.name,
            'price_unit': product_obj.price,
            'product_uom_qty': 1,
            'customer_lead': 30,
            'company_id': self.company_id.id,
        }
        order_line_object = self.env['sale.order.line'].create(val)
        self.write({'order_line': [(4, order_line_object.id)]})
        order_line_object._onchange_discount()

    def convert_length(self, length):
        print('this is length', length)
        if length <= 0:
            raise UserError('Length can not be 0 or less')
        elif 0 < length <= 0.47:
            return length
        elif 0.47 < length <= 0.50:
            return 0.50
        elif 0.50 < length <= 0.55:
            return 0.55
        elif 0.55 < length <= 0.60:
            return 0.60
        elif 0.60 < length <= 0.65:
            return 0.65
        elif 0.65 < length <= 0.75:
            return 0.75
        elif 0.75 < length <= 0.80:
            return 0.80
        elif 0.8 < length <= 1:
            return 1
        elif 1 < length <= 1.20:
            return 1.20
        elif 1.20 < length <= 1.50:
            return 1.50
        elif 1.50 < length <= 1.60:
            return 1.60
        elif 1.60 < length <= 1.9:
            return 1.9
        elif 1.90 < length <= 2:
            return 2
        else:
            return length
        # else :
        #     self.length = 0

    def convert_width(self, width):
        print('this is width', width)
        if width <= 0:
            return UserError('Width can not be 0 or less')
        elif 0 < width <= 0.470:
            return width
        elif 0.47 < width <= 0.50:
            return 0.50
        elif 0.50 < width <= 0.55:
            return 0.550
        elif 0.550 < width <= 0.60:
            return 0.60
        elif 0.60 < width <= 0.65:
            return 0.65
        elif 0.65 < width <= 0.75:
            return 0.75
        elif 0.75 < width <= 0.80:
            return 0.80
        elif 0.80 < width <= 1:
            return 1
        elif 1 < width <= 1.20:
            return 1.20
        elif 1.20 < width <= 1.50:
            return 1.50
        elif 1.50 < width <= 1.60:
            return 1.60
        elif 1.60 < width <= 1.80:
            return 1.80
        elif 1.80 < width <= 1.90:
            return 1.90
        elif 1.90 < width <= 2.00:
            return 2.00
        else:
            return width

    def find_heigth(self, height):
        print('this is width', height)
        if height <= 0:
            return UserError('Value can not be 0 or less')
        elif 0 < height <= 6:
            return 6
        elif 6 < height <= 12:
            return 12
        elif 12 < height <= 16:
            return 16
        elif 16 < height <= 20:
            return 20
        elif 20 < height <= 24:
            return 24
        else:
            return 24
    def cleanup(self):
        self.height = 1
        self.width = 1
        self.length = 1
        self.foam_unit_price = 0
        self.fabric_unit_price = 0
