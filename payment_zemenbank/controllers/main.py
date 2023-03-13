import json
import logging
import pprint
import werkzeug
import werkzeug.utils
import requests
from odoo import http, _
from odoo.http import request

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ZemenbankController(http.Controller):
    _accept_url = '/payment/zemenbank/return/'

    @http.route([
        '/payment/zemenbank/return', 
    ],  type='json', auth='public', methods=['POST'], csrf=False)
    def zemen_return(self, **kw):
        _logger.info("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
        _logger.info(kw)
        # data = {
        #     "params" : { "status": "PAID", 
        #                  "id": "6256c307fe8251024f69e718", 
        #                  "trace_no": "0000200215", 
        #                  "amount": '10.00', 
        #                  "issued_to": '+251921388357', 
        #                  "appId": '1234', 
        #                  "session": 'e185a920-bb25-11ec-b121-752b793d4d2a', 
        #                  "created_date": "2022-04-13T12:33:11.352Z", 
        #                  "successIndicator": '777f325108c842a4' 
        #                 }
        # }
        # headers = {"Content-Type": "application/json"}
       
        _logger.info('Beginning Zemen Bank form_feedback with post data %s', pprint.pformat(kw))  # debug
        if kw is not None:
            _logger.info("mmmmmmmm")
            #request.env['payment.transaction'].sudo()._return_value_from_zemen_bank(kw)
            
            # _logger.info("afterrrrrrrrrrrrrrrrrrrrrrrrrrr")
            request.env['payment.transaction'].sudo().form_feedback(kw, 'zemen_bank')
            # res = requests.post(f"http://localhost:8069/payment/process", json={}, data=json.dumps(data),headers=headers)
            
            # return werkzeug.utils.redirect(ref_url)
        return werkzeug.utils.redirect('/payment/process')




    @http.route([
        '/payment/zemenbank/feedback',
    ], type='http', auth='public', csrf=False)
    def zemenbank_form_feedback(self, **post):
        _logger.info('Beginning form_feedback with post data %s', pprint.pformat(post))  # debug
        request.env['payment.transaction'].sudo().form_feedback(post, 'zemen_bank')
        return werkzeug.utils.redirect('/payment/process')



    @http.route('/zemepayement_returnlllllll', type='json', method=['POST'], auth='public', website=True, csrf=False)
    def zemen_bank_payement_return(self, **kw):
        _logger.info("######## zemen bank hosted payment page")
        
        _logger.info(kw)
        # _logger.info(json.load(kw))
        _logger.info(kw['reference'])
        # _logger.info(kw.json())
        # data = kw
        data = {"params" : {
            'phone': kw['phone'],
            'payement_token_id': kw['amount'],
            'acquirer_id': kw['amount'],
            'reference': kw['reference'],
            'payment': kw['amount'],
            'paymentToken': "ABBBBB",
            'acquirer_id': '00001'
            } 
           
        }
        _logger.info("#####data %s", data)
        headers = {"Content-Type": "application/json"}
        
        
        
        res = requests.post(f"http://localhost:8069/get_values", json={}, data=json.dumps(data),headers=headers)
        
        _logger.info(" ||||||||||||||    returned respose from zemen bank")
        response = res.json()
        _logger.info(response)
        # if response['result']['Success'] == True:
        #     request.env['payment.transaction'].sudo().form_feedback(data, 'zemen')
        # return werkzeug.utils.redirect('/payment/process')
        return response
       
        
        
        

    @http.route('/zemen_bank_payment_return', type='json',method=['POST'],  auth='public', website=True, csrf=False)
    def zemen_bank_payment_return(self, **kwargs):
        _logger.info("######## Payment Return  from zemen bank")
        _logger.info(kwargs)
        _logger.info('Beginning Zemen Bank form_feedback with post data %s', pprint.pformat(kwargs))  # debug
        # if post.get('authResult') not in ['CANCELLED']:
        #         request.env['payment.transaction'].sudo().form_feedback(post, 'zemen_bank')
        # return werkzeug.utils.redirect('/payment/process')
        # _logger.info(post['merchantReference'])
        # _logger.info(post['id'])
        # values = post.get('values')
        ref = kwargs['reference']
        if kwargs['reference'] != 0:
            _logger.info("   ####  merchantReference valied")
            # pt = request.env['sale.order'].search([], order="name desc")
            payment = request.env['res.users'].sudo().search([], limit=2)
            _logger.info(payment)
            pt = request.env['payment.transaction'].sudo().search([], limit=10)
            _logger.info("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
            _logger.info(pt)
            # res = request.env['payment.acquirer'].sudo().zemen_get_form_action_url(post, 'zemen_bank')
            # _logger.info(res)
            # self._value_update()
            # _logger.info(pt.reference)
            response = [
                {
                    "message": "Invoice add successfully",
                    "success": "True",
                    "data": {
                        # "urls": "http://localhost:8069/checking?#scrollTop=0"
                        
                        "urls": "https://www.jotform.com/form/220951758815565#preview"
                       
                    }
                    

                }
                
            ]
            
            return response[0]
        else:
            response = [
               
                {
                    "ErrorDetail": "received data with missing reference",
                    "ShortMessage": "Detail Error Message",
                    "Success": "False"
                }
            ]
        
            return response[0]
  