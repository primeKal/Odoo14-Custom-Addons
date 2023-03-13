from odoo.exceptions import ValidationError
from odoo import api, fields, models
from openerp.http import request

from odoo.exceptions import UserError

import json
from werkzeug import urls
import pprint

import logging

_logger = logging.getLogger(__name__)


class BoaPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[
        ('boa', 'Abyssiniya Bank')
    ],  ondelete={'boa': 'set default'})

    boa_app_id = fields.Char(string= 'BOA Bank AppId',
                                   required_if_provider='boa',
                                   groups='base.group_user')
    url = fields.Char(string= 'BOA Bank Url',
                                   required_if_provider='boa',
                                   groups='base.group_user')
    @api.model
    def _get_boa_urls(self):
        """ Atom URLS """
        return {
            'boa_form_url': '/begin3'
        }

    def boa_get_form_action_url(self):
        return self._get_boa_urls()['boa_form_url']

    def boa_form_generate_values(self, values):
        _logger.info(
            'BOA : preparing all form values to send to BOA form url')
        request_string = self.validate_data(values)
        request_string['boa_app_id'] = self.boa_app_id

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        request_string.update({

            # 'products': product_list,
            'return_url': urls.url_join(base_url, '/returnUrl3'),
            "url": self.url
        })
        return request_string

    # def get_products(self, reference):
    #     txs = self.env['payment.transaction'].search([('reference', '=', reference)])
    #     txs[0].currency_id = self.company_id.currency_id
    #     sale_order = txs[0].sale_order_ids
    #     if sale_order:
    #         products = sale_order[0].website_order_line
    #         if not products:
    #             raise UserError('Please Add Products')
    #     else:
    #         invoice_orders = txs[0].invoice_ids
    #         invoice_line = invoice_orders.invoice_line_ids
    #         products = invoice_line.product_id
    #     product_list = []
    #     x = 0
    #     for product in products:
    #         print(product.name)
    #         try:
    #             quantity = product.product_uom_qty
    #         except:
    #             quantity = invoice_line[x].quantity
    #         product_list.append({"name": product.name,
    #                              "quantity": quantity})
    #         x = x + 1
    #     product_list = json.dumps(product_list)
    #     print(product_list)
    #     return product_list

    def validate_data(self, values):
        _logger.info(
            'BOA : Validating all form data')
        if  not values['partner_phone'] \
                or values['amount'] == 0 \
                or not values['reference']:
            raise UserError(
                'Please Insert all available information about customer' + 'phone \n  '
                                                                           ' amount')

        request_string = {
            "phone": values['partner_phone'],
            "app_order_id": values['reference'],
            "totalAmount": values['amount'],
            "boa_app_id": values['boa_app_id'],

        }

        return request_string


class PaymentTransactionBOA(models.Model):
    _inherit = 'payment.transaction'

    boa_txn_type = fields.Char('Transaction type')

    @api.model
    def _boa_form_get_tx_from_data(self, data):
        if data.get('tx_ref') :
            tx_ref = data.get('tx_ref')
        else :
            tx_ref = data.get('data').get('tx_ref')
        txs = self.search([('reference', '=', tx_ref)])
        return txs

    def _boa_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    def _boa_form_validate(self, data):
        _logger.info(
            'BOA: Validate transaction pending or done')
        try :
            succ = data['success']
            if succ:
                tx_ref = data.get('tx_ref')
                res = {
                    'acquirer_reference': tx_ref,
                    'boa_txn_type': 'BOA Payment'
                }
                # self._set_transaction_done()
                self.write(res)
                _logger.info(
                    'BOA: Done when called transaction done from notify URL')
                return True
            else:
                tx_ref = data.get('tx_ref')
                res = {
                    'acquirer_reference': tx_ref,
                    'boa_txn_type': 'BOA Payment'
                }
                # self._set_transaction_canceled()
                self.write(res)
                _logger.info(
                    'BOA: Done when called transaction done from notify URL')
                return True
        except :
            tx_ref = data.get('tx_ref')
            res = {
                'acquirer_reference': tx_ref,
                'boa_txn_type': 'BOA Payment'
            }
            self.write(res)
            _logger.info(
                'BOA: Done when called transaction done from notify URL')
            return True



