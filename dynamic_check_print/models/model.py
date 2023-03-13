from odoo import fields, models, api, registry, sql_db, _, modules
from odoo.exceptions import UserError
from odoo.tools.image import image_data_uri
from base64 import decodebytes
import urllib.request
from io import BytesIO, StringIO
import io, base64
from PIL import Image
# from PIL import Image
import base64

from datetime import date


class CheckWizzz(models.TransientModel):
    _name = "check.wiz"
    _description = "A Wizard for productssss"

    def _to(self):
        active = self._context.get('active_id')
        print(active)
        user = self.env["account.payment"].browse(active)
        print(user.partner_id)
        number = user.partner_id.display_name
        if (number == False):
            number = 'No partner'
        return number
    def amount(self):
        active = self._context.get('active_id')
        print(active)
        user = self.env["account.payment"].browse(active)
        number = user.amount
        if (number == False):
            number = ''
        return number
    def amount_word(self):
        active = self._context.get('active_id')
        print(active)
        user = self.env["account.payment"].browse(active)
        number = user.check_amount_in_words
        if (number == False):
            number = ''
        return number
    def date_now(self):
        today = date.today()
        d1 = today.strftime("%d/%m/%Y")
        return d1



    var_1 = fields.Char('To', default=_to)
    var_2 = fields.Char('Amount', default=amount )
    var_3 = fields.Char('Amount Word', default= amount_word)
    var_4 = fields.Char('Date', default= date_now)
    check = fields.Many2one('check.data', String='Check Template')

    def print222(self):
        print('printingggg')
        print('here to get starteddddddddddd')
        dd = self.env.ref('dynamic_check_print.action_student_id_card')
        print(dd.name)
        print('fffffffffffffffffffffffffff')
        dds = {
            'data': self
        }
        print(self)
        return dd.report_action(self)

    @api.model
    def create(self, vals):
        res = super(CheckWizzz, self).create(vals)
        return res


from PIL import Image, ImageDraw, ImageFont
from pytesseract import pytesseract


class ProductsDemo(models.Model):
    _name = "check.data"
    _description = "A model for check data"

    name = fields.Char('Bank Name')
    first = fields.Char('To Name')
    first_location_x = fields.Char('First Left')
    first_location_y = fields.Char('First Top')

    second = fields.Char('Amount')
    second_location_x = fields.Char('Second Left')
    second_location_y = fields.Char('Second Top ')

    third = fields.Char('Amount in Words')
    third_location_x = fields.Char('Third Left ')
    third_location_y = fields.Char('Third  Top')

    fourth = fields.Char('Date')
    fourth_location_x = fields.Char('Fourth Left')
    fourth_location_y = fields.Char('Fourth Top')

    img = fields.Binary('Check Image', attachment=True, help='Please add a clear picture')

    tesseract_adress = fields.Char('Tesseract')
    status = fields.Selection([
        ('validated', 'validated'),
        ('draft', 'draft')
    ])

    @api.model
    def create(self, vals):
        print('----------------------------starting-----------------------------------------')
        res = super(ProductsDemo, self).create(vals)
        attachemnt = self.env['ir.attachment'].search(
            [('res_model', '=', 'check.data'), ('res_field', '=', 'img'), ('res_id', '=', res.id)])
        decoded_img = base64.b64decode(attachemnt.datas)
        decoded_img_id = io.BytesIO(decoded_img)
        img = Image.open(decoded_img_id)
        width = img.width 
        print(width)
        height = img.height
        print(height)
        img = img.resize((width,height))
        pytesseract.tesseract_cmd = res.tesseract_adress
        text = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        print(text)
        index = int(0)
        data = {}
        for tex in text['text']:
            if tex == res.first:
                data['first_location_x'] = text['left'][index]
                data['first_location_y'] = text['top'][index]
            if tex == res.second:
                data['second_location_x'] = text['left'][index]
                data['second_location_y'] = text['top'][index]
            if tex == res.third:
                data['third_location_x'] = text['left'][index]
                data['third_location_y'] = text['top'][index]
            if tex == res.fourth:
                data['fourth_location_x'] = text['left'][index]
                data['fourth_location_y'] = text['top'][index]
            index += 1
        res.write(data)
        return res

    def generate_pic(self):
        print('here to get starteddddddddddd')
        attachemnt = self.env['ir.attachment'].search(
            [('res_model', '=', 'check.data'), ('res_field', '=', 'img'), ('res_id', '=', self.id)])
        decoded_img = base64.b64decode(attachemnt.datas)
        decoded_img_id = io.BytesIO(decoded_img)
        img = Image.open(decoded_img_id)
        d = ImageDraw.Draw(img)
        fnt = ImageFont.truetype("comicbd.ttf", 20)
        d.text((int(self.first_location_x) + 100, int(self.first_location_y) - 25), self.first, font=fnt,
               fill=(255, 69, 0))
        d.text((int(self.second_location_x) + 50, int(self.second_location_y) - 25), self.second, font=fnt,
               fill=(255, 69, 0))
        d.text((int(self.third_location_x) + 50, int(self.third_location_y) - 25), self.third, font=fnt,
               fill=(255, 69, 0))
        img.save('Abb_New2.jpg')
        byteIO = io.BytesIO()
        img.save(byteIO, format='PNG')
        byteArr = byteIO.getvalue()

        # encode
        result = base64.b64encode(byteArr)
        # get base url
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        attachment_obj = self.env['ir.attachment']
        # create attachment
        attachment_id = attachment_obj.create(
            {'name': "name", 'datas': result})
        # prepare download url
        download_url = '/web/content/' + str(attachment_id.id) + '?download=true'
        # download
        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }
