from odoo.exceptions import ValidationError
from odoo import api, fields, models
from openerp.http import request


import logging

_logger = logging.getLogger(__name__)


class PaymentAggrigatorModel(models.Model):
    _name= 'aggrigator.payer'
    type = fields.Selection([
        ('telebirrussd','TelebirrUssd'),
        ('telebirrh5','TelebirrH5'),
        ('zemen', 'Zemen'),
        ('boa', 'BOA Card'),
        ('amole','Amole'),
        ('hellocash', 'HelloCash')
    ],string='Type', required=True )
    state = fields.Selection([
        ('test','test'),
        ('prod','prod')
    ],string='State', )
    name = fields.Char('Name')
    who = fields.Many2one('res.company')
    ip = fields.Char('IP Address')
    url = fields.Char('Payment Url')


    # required for telebirr ussd
    callBack = fields.Char('Your Return Url', required_if_type='TelebirrUssd')
    callerId = fields.Char('YOur caller Id',required_if_type='TelebirrUssd')
    callerPin = fields.Char('Your caller PIN',required_if_type='TelebirrUssd')
    callerEncryptedPassword = fields.Char('Your Password',required_if_type='TelebirrUssd')
    shortCode = fields.Char('Your Short Code',required_if_type='TelebirrUssd')

    # required for telebirr route
    # telebirr_shortcode =fields.Char("Telebirr ShortCode")



    # required for zemen payment gateways
    merchant = fields.Char('Merchant', required_if_type='Zemen')
    apiUsername = fields.Char('Username', required_if_type='Zemen')
    apiPassword = fields.Char('Password', required_if_type='Zemen')
    callback = fields.Char('Callback', required_if_type='Zemen')
    js_url = fields.Char('JS Url', required_if_type='Zemen')
    callback_type = fields.Selection([
        ('redirect','Redirect'),
        ('request','Request'),
    ],string='Callback Type', default='redirect')


    # required for boa card
    profile_id = fields.Char('Profile ID')
    access_key = fields.Char('Access Key')
    secret_key = fields.Char('Secret Key')
    callack_boa = fields.Char('Callback')


    # required for amole
    fetan_meerchant_id =  fields.Char('Fetan Merchant Id')
    hdr_signiture =  fields.Char('HDR Signiture')
    hdr_username = fields.Char('HDR Username')
    hrd_password = fields.Char('HDR password')
    hrd_ipaddress = fields.Char('HDR IP')


    # required for hello cash
    hello_username = fields.Char('HelloCash Username')
    hello_password = fields.Char('HelloCash Password')
    hello_system = fields.Char('HelloCash System')


class PaymentAggrigatorTransactionModel(models.Model):
    _name= 'aggrigator.transaction'

    trace_no = fields.Char('Trace Number', required=True)
    amount = fields.Float('Amount', required=True)
    to = fields.Char('To', required=True)

    state = fields.Selection([
        ('draft','draft'),
        ('pending','pending'),
        ('confiremed', 'confiremed'),
        ('failed', 'Failed')
    ],string='Type', default= 'draft')
    payer = fields.Many2one('aggrigator.payer', string="Payment Model", required=True)
    type= fields.Char('Type',compute='_type_set')
    session = fields.Char('Session(Zemen Only)')
    amole_code = fields.Char('Code(Amole Only)')

    success_indicator = fields.Char('Success Indicator-zemenonly')


    def _type_set(self):
        for rec in self:
            rec.type = rec.payer.type
