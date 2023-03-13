from odoo.exceptions import ValidationError
from odoo import api, fields, models
from openerp.http import request

from odoo.exceptions import UserError

import json
from werkzeug import urls
import pprint

import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirerThawani(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[
        ('zemen', 'zemen')
    ], default='zemen', ondelete={'zemen': 'set default'})

    zemen_app_id = fields.Char(string= 'Zemen Bank AppId',
                                   required_if_provider='zemen',
                                   groups='base.group_user')



    @api.model
    def _get_zemen_urls(self):
        """ Atom URLS """
        return {
            'zemen_form_url': '/begin2'
        }

    def zemen_get_form_action_url(self):
        return self._get_zemen_urls()['zemen_form_url']

    def zemen_form_generate_values(self, values):
        _logger.info(
            'ZEMEN : preparing all form values to send to ZEMEN form url')
        # product_list = self.get_products(values['reference'])
        request_string = self.validate_data(values)
        request_string['zemen_app_id'] = self.zemen_app_id

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        request_string.update({

            # 'products': product_list,
            'return_url': urls.url_join(base_url, '/returnUrl')
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
            'ZEMEN: Validating all form data')
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
            # "zemen_app_id": values['zemen_app_id'],
        }

        return request_string


class PaymentTransactionZemen(models.Model):
    _inherit = 'payment.transaction'

    zemen_txn_type = fields.Char('Transaction type')

    @api.model
    def _zemen_form_get_tx_from_data(self, data):
        if data.get('tx_ref') :
            tx_ref = data.get('tx_ref')
        else :
            tx_ref = data.get('data').get('tx_ref')
        txs = self.search([('reference', '=', tx_ref)])
        return txs

    def _zemen_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        return invalid_parameters

    def _zemen_form_validate(self, data):
        _logger.info(
            'ZEMEN: Validate transaction pending or done')
        try :
            succ = data['success']
            if succ:
                tx_ref = data.get('tx_ref')
                res = {
                    'acquirer_reference': tx_ref,
                    'zemen_txn_type': 'Zemen Payment'
                }
                # self._set_transaction_done()
                self.write(res)
                _logger.info(
                    'ZEMEN: Done when called transaction done from notify URL')
                return True
            else:
                tx_ref = data.get('tx_ref')
                res = {
                    'acquirer_reference': tx_ref,
                    'zemen_txn_type': 'Zemen Payment'
                }
                # self._set_transaction_canceled()
                self.write(res)
                _logger.info(
                    'ZEMEN: Done when called transaction done from notify URL')
                return True
        except :
            tx_ref = data.get('tx_ref')
            res = {
                'acquirer_reference': tx_ref,
                'zemen_txn_type': 'Zemen Payment'
            }
            self.write(res)
            _logger.info(
                'ZEMEN: Done when called transaction done from notify URL')
            return True



