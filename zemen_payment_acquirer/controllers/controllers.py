import json
import logging
import requests
import werkzeug
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from werkzeug import urls

import pprint

_logger = logging.getLogger(__name__)


class ZemenBank(http.Controller):
    global private
    global tx_ref

    @http.route('/notifyUrl2',
                type='http', auth='public', csrf=False, methods=['GET', 'POST'], save_session=False)
    def zemenReturn(self, **post):
        _logger.info('---------------------------this is returninggggg')
        _logger.info(post)
        request.env['payment.transaction'].sudo().form_feedback(post, 'zemen')
        return werkzeug.utils.redirect('/payment/process')

        # verify_url = "https://api.chapa.co/v1/transaction/verify/" + self.tx_ref
        # request_headers = {
        #         "Authorization": "Bearer " + str(self.private)
        # }
        # print(self.private)
        # try :
        #     res = requests.get(verify_url,headers=request_headers)
        # except Exception as e:
        #     print(e)
        #
        # _logger.info(
        #     'Chapa: entering form_feedback from retrun or notify with post data %s', pprint.pformat(post))
        # if res.status_code == 200:
        #     data = dict(res.json())
        #     request.env['payment.transaction'].sudo().form_feedback(data, 'zemen')
        # return werkzeug.utils.redirect('/payment/process')

    @http.route('/returnUrl2',
                type='json', auth='public', csrf=False, methods=['POST', 'GET'], save_session=False)
    def zemenReturning(self,**kwargs):
        post = request.jsonrequest
        _logger.info(post)
        post.update({
            'tx_ref': self.tx_ref,
            'success': post['success']
        })
        _logger.info(
            'ZEMEN: entering form_feedback from successful payment and returning(redirecting) ')
        _logger.info(post)
        request.env['payment.transaction'].sudo().form_feedback(post, 'zemen')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/begin2', type='http', auth='public', csrf=False, methods=['POST'])
    def begin_transaction(self, **post):
        _logger.info(
            'ZEMEN : Begining to parse data and post to request URL')
        # request_url = 'https://pgw.shekla.app/zemen/post_bill'
        # request_url = 'http://localhost:8069/send_sms'
        # request_url = 'http://178.128.194.65:8069/zemen/postbill'
        # request_url = 'http://localhost:8069/zemen/postbill'
        request_url = 'http://196.189.44.60:8069/zemen/postbill'
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.tx_ref = post['app_order_id']
        request_headers = {
            # "Authorization" : "Bearer " + post["private_key"],
            "Content-Type": "application/json",
        }
        # print(post['products'])
        # print(json.dumps(post['products']))
        # lets make a trace number following 'unique random number_ordernumber pattern'
        order_id = post['app_order_id']
        if '-' in order_id:
            temp = order_id.split('-')
            order_id = temp[0][1:]+temp[1] + '_' + str(temp[0])[1:]
        else :
            order_id = str(00) + '_' + order_id[1:]
        total =  round(float(post["totalAmount"]),3)
        # trace_number = str(post['app_order_id'][1:]) + '_' + str(post['app_order_id'][1:])
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        req_data = {
            "amount": round(float(post['totalAmount']),2),
            "phone": post['phone'],
            "description": post['app_order_id'],
            "code": "0005",
            'reference': post['app_order_id'],
            'trace_no': order_id,
            # 'trace_no': '150381222_150380222',
            'app_id': post['zemen_app_id'],
            'payer_id': post['zemen_app_id'],
            # 'appId': '1234'
            'return_url': str(urls.url_join(base_url, "/returnUrl2"))
        }
        # return werkzeug.utils.redirect('/returnUrl2')
        _logger.info('------------------------hi-------------------------')
        _logger.info(req_data)
        _logger.info(request_url)
        try:
            _logger.info('------------------------hi222-----------------')
            response = requests.post(request_url, headers=request_headers, json=req_data)
        except Exception as e:
            _logger.info('-----------------------h3--------------------------')
            _logger.info(e)
            print(e)
            return 'Error Occured'
        if response.status_code >= 200 and response.status_code <= 300:
            _logger.info(
                'ZEMEN : Success in post request, set transaction to pending and redirect to new Transaction Url')
            response_json = response.json()
            post.update({
                'tx_ref': post['app_order_id']
            })
            request.env['payment.transaction'].sudo().form_feedback(post, 'zemen')
            data = response_json['result']['data']
            return werkzeug.utils.redirect(response_json['result']["data"]['toPayUrl'])
        else:
            return http.request.render('http_routing.http_error',{
                'status_code': response.status_code,
                'status_message' : response.content
            })
            # raise werkzeug.exceptions.BadRequest(
            #     "Request not successful,Please check the keys or consult the admin.code-" + str(response.status_code))
            # return response.status_code
