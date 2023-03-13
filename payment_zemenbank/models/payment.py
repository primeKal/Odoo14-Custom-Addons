# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

import json
import logging
import pprint
import werkzeug
import werkzeug.utils
import requests

from odoo import api, fields, models, tools, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_zemenbank.controllers.main import ZemenbankController
from odoo.tools.pycompat import to_text


from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

_logger = logging.getLogger(__name__)

CURRENCY_CODE_MAPS = {
    "ETB": 2,
    "EUR": 2,
    "AED": 2,
    "AUD": 2,
    "USD": 2,
    "ZAR": 3,
    
}

class ZemenbankPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[
        ('zemenbank', 'Zemen Payment')
    ], default='zemenbank', ondelete={'zemenbank': 'set default'})
    zemenbank_email_account = fields.Char('Email', required_if_provider='zemenbank', groups='base.group_user')
    zemenbank_seller_account = fields.Char(
        'Merchant Account ID', groups='base.group_user',
        help='The Merchant ID is used to ensure communications coming from Zmenbank are valid and secured.')
    
    zemen_secret_key = fields.Char(string= 'Zemenbank Private Key', required_if_provider='zemenbank',groups='base.group_user')
    zemen_publishable_key = fields.Char(string='Zemenbank Public Key', required_if_provider='zemenbank', groups='base.group_user')
    # zemen_secret_key = fields.Char('Zemen Private Key', required_if_provider='zemenbank',
    #                                    groups='base.group_user')
    # zemen_publishable_key = fields.Char('Zemen Public Key', required_if_provider='zemenbank',
    #                                   groups='base.group_user')

    @api.model
    def _zemen_convert_amount(self, amount, currency):
        """
        Zemen bank requires the amount to be multiplied by 10^k,
        where k depends on the currency code.
        """
        k = CURRENCY_CODE_MAPS.get(currency.name, 2)
        paymentAmount = int(tools.float_round(amount, k) * (10**k))
        _logger.info("||||||||||||||||||||||||||||||| %s", paymentAmount)
        _logger.info(amount)
        return amount

    return_url = "global"
    return_url = []
    
    def zemenbank_form_generate_values(self, values):
        _logger.info("############# method one Form generete values ############")
        base_url = self.get_base_url()
        _logger.info(base_url)
        # tmp
        import datetime
        from dateutil import relativedelta

        paymentAmount = self._zemen_convert_amount(values['amount'], values['currency'])
        if self.provider == 'zemenbank':
            tmp_date = datetime.datetime.today() + relativedelta.relativedelta(days=1)

            values.update({
                'merchantReference': values['reference'],
                'paymentAmount': '%d' % paymentAmount,
                'currencyCode': values['currency'] and values['currency'].name or '',
                'shipBeforeDate': tmp_date.strftime('%Y-%m-%d'),
                # 'skinCode': self.zemen_skin_code,
                # 'merchantAccount': self.zemen_merchant_account,
                'shopperLocale': values.get('partner_lang', ''),
                'sessionValidity': tmp_date.isoformat('T')[:19] + "Z",
                # 'resURL': urls.url_join(base_url, ZemenController._accept_url),
                # 'merchantReturnData': json.dumps({'return_url': '%s' % values.pop('return_url')}) if values.get('return_url', '') else False,
                'shopperEmail': values.get('partner_email') or values.get('billing_partner_email') or '',
            })
            
            
            _logger.info("##############genereted values")
            # _logger.info(values)
            # data =   {
            #
            #         "phone": values['partner_phone'],
            #         "description":"ZMallBnak Test Order Payment",
            #         "amount": values['amount'],
            #         "trace_no":"00138_SO138",
            #         "appId":"1234",
            #         "returnUrl":"/"
            #         }
           
            data = {"params" : { 
                                        "phone": values['partner_phone'],
                                        "description": values['reference'],
                                        "code": "0005",
                                        # 'merchantAccount': self.zemen_merchant_account,
                                        "amount": values['paymentAmount'],
                                        # "trace_no": values['reference'],
                                        # "appId": "1234"
                                        # 'resURL': urls.url_join(base_url, ZemenController._accept_url),
                                        'reference': values['reference'],
                                        
                                        
                                       } }
            headers = {"Content-Type": "application/json"}
            _logger.info("########### controller value ")
            # res = requests.post(f"https://pgw.shekla.app/zemen/post_bill",  json=data ,headers=headers)
            
            res = requests.post(f"http://localhost:8069/zemen_bank_payment_return",  json={}, data=json.dumps(data),headers=headers)
            # _logger.info("########### controller value ")
            # _logger.info(res)
            _logger.info("-------------------Return Response  From Zemen ------------------------------------")
            global return_url
            return_url = []
            _logger.info(res.json())
    
            
            # response = res.json()
            # _logger.info(response) 
            # _logger.info(response['success'])
            # _logger.info(response['data']['data']['toPayUrl'])
            
            response = res.json()
            response = response['result']
            _logger.info(response) 
            _logger.info(type(response))
            # for k,v in response:
            #     _logger.info(f"{k}: {v}")
                
            _logger.info(response['success'])
            _logger.info(response['data']['urls'])
            
            
            if response['success']:
                
                _logger.info("EEEEEEEEEEEEEEEEEEE")
                # request.env['payment.transaction'].sudo().form_feedback(values, 'zemen_bank')
                vals = response['data']['urls']
                _logger.info(response['data'])
                
                # vals = response['data']['data']['toPayUrl']
                
                return_url.append((vals))
                _logger.info(return_url)
                # request.env['payment.acquirer'].sudo()._get_zemen_bank_urls(vals)
                # return werkzeug.utils.redirect('/popup/campaign')
                # res = request.env['payment.transaction'].sudo().form_feedback(data, 'zemen_bank')
                
                
            # _logger.info(response['result']['merchantReference'])
            # pt = request.env['payment.transaction'].sudo().search([('reference','=', response['result']['merchantReference'])])
            # _logger.info(pt)
            # _logger.info(pt.reference)
            # _logger.info(pt.payment_id)
            
            
            
            # v = []
            # if len(pt) != 0:
            #     for vals in pt:
            #         vv = {}
            #         vv['acquirer_id'] = '0000002'
            #         # vals.update({
            #             # 'payment_id': '12452',
            #             # 'payment_token_id': '12345',
            #             # 'acquirer_id': '0000002',
            #             # 'date': datetime.now()
            #         # })
            #     v.append(vv) 
            #     _logger.info("ddddddddddddddd %s", v)
            # pass
           
        else:
            tmp_date = datetime.date.today() + relativedelta.relativedelta(days=1)

            values.update({
                'merchantReference': values['reference'],
                'paymentAmount': '%d' % paymentAmount,
                'currencyCode': values['currency'] and values['currency'].name or '',
                'shipBeforeDate': tmp_date,
                # 'skinCode': self.zemen_skin_code,
                # 'merchantAccount': self.zemen_merchant_account,
                'shopperLocale': values.get('partner_lang'),
                'sessionValidity': tmp_date,
                # 'resURL': urls.url_join(base_url, ZemenController._accept_url),
                # 'merchantReturnData': json.dumps({'return_url': '%s' % values.pop('return_url')}) if values.get('return_url') else False,
            })
           
          
            
        return values
    
    
    def zemenbank_get_form_action_url(self):
        _logger.info("22222222222222222222")
        
        # return  '/payment/zemenbank/feedback'
        
        return return_url[0] , '/payment/zemenbank/feedback'

    def _format_zemenbank_data(self):
        _logger.info("333333333333333333333333")
        
        company_id = self.env.company.id
        # filter only bank accounts marked as visible
        journals = self.env['account.journal'].search([('type', '=', 'bank'), ('company_id', '=', company_id)])
        accounts = journals.mapped('bank_account_id').name_get()
        bank_title = _('Bank Accounts') if len(accounts) > 1 else _('Bank Account')
        bank_accounts = ''.join(['<ul>'] + ['<li>%s</li>' % name for id, name in accounts] + ['</ul>'])
        post_msg = _('''<div>
                    <h3>Please use the following zemenbank details</h3>
                    <h4>%(bank_title)s</h4>
                    %(bank_accounts)s
                    <h4>Communication</h4>
                    <p>Please use the order name as communication reference.</p>
                    </div>''') % {
                    'bank_title': bank_title,
                     'bank_accounts': bank_accounts,
        }
        return post_msg

    @api.model
    def create(self, values):
        _logger.info("44444444444444444 create function")
        
        """ Hook in create to create a default pending_msg. This is done in create
        to have access to the name and other creation values. If no pending_msg
        or a void pending_msg is given at creation, generate a default one. """
        if values.get('provider') == 'zemenbank' and not values.get('pending_msg'):
            values['pending_msg'] = self._format_zemenbank_data()
        return super(ZemenbankPaymentAcquirer, self).create(values)

    def write(self, values):
        _logger.info("55555555555555 write function")
        
        """ Hook in write to create a default pending_msg. See create(). """
        if not values.get('pending_msg', False) and all(not acquirer.pending_msg and acquirer.provider != 'zemenbank' for acquirer in self) and values.get('provider') == 'zemenbank':
            values['pending_msg'] = self._format_zemenbank_data()
        return super(ZemenbankPaymentAcquirer, self).write(values)
    
    def action_click():
        pass


class ZemenbankPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    
    order_reference = fields.Char("Order Reference");

    @api.model
    def _zemen_bank_form_get_tx_from_data(self, data):
        _logger.info("####### zemen_bank  Get Transaction From Data #########")
        _logger.info(data)
        
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx = self.search([('reference', '=', reference)])

        _logger.info("####### tx: %s",tx)
        if not tx or len(tx) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return tx
    
    
    

    def _zemen_bank_form_get_invalid_parameters(self, data):
       
        _logger.info("################# Checking  Get invalid parameters ################")
        _logger.info(data)
        
        invalid_parameters = []
       
        # if self.acquirer_reference and data.get('trace_no') != self.acquirer_reference:
        #     invalid_parameters.append(('trace_no', data.get('trace_no'), self.acquirer_reference))

         # check buyer
        _logger.info("  **********  check payment token id*********")
        _logger.info(data.get('payer_id'))
        if self.payment_token_id and data.get('payer_id') != self.payment_token_id.acquirer_ref:
            invalid_parameters.append(('payer_id', data.get('payer_id'), self.payment_token_id.acquirer_ref))
       
       
        
        if float_compare(float(data.get('amount') or '0.0'), self.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % self.amount))
        # if data.get('currency') != self.currency_id.name:
        #     invalid_parameters.append(('currency', data.get('currency'), self.currency_id.name))

        return invalid_parameters

    def _zemen_bank_form_validate(self, data):
        _logger.info("################# Checking  Validate state change ################")
        
        _logger.info('Validated zemenbank payment for tx %s: set as pending' % (self.reference))
        self._set_transaction_pending()
        
     
        
        status = data.get('status', 'PENDING')
        if status == 'PAID': 
            _logger.info("*********under paid status**********")
            # self.write({'acquirer_reference': data.get('trace_no')})
            self.write({'acquirer_reference': data.get('reference')})
            # self.write({'payment_token_id': data.get('payer_id')})
            self._set_transaction_done() 
            return True
        elif status == 'PENDING':
            self.write({'acquirer_reference': data.get('trace_no')})
            self._set_transaction_pending()
            return True
        else:
            error = _('Zemen Bank: feedback error')
            _logger.info(error)
            self.write({'state_message': error})
            self._set_transaction_cancel()
            return False
    
        return True
    
class PaymentToken(models.Model):
    _inherit = 'payment.token'

    zemenbank_payment_method_type = fields.Char(string='PaymentMethod Type')

    
  
    