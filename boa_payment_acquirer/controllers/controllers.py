import json
import logging
import requests
import werkzeug
from odoo import http
from odoo.http import request
import uuid
from odoo.exceptions import UserError
from werkzeug import urls

import pprint

_logger = logging.getLogger(__name__)


class BOAPayemntController(http.Controller):
    global private
    global tx_ref

    @http.route('/notifyUrl',
                type='http', auth='public', csrf=False, methods=['GET', 'POST'], save_session=False)
    def boa_return(self, **post):
        # if res.status_code == 200:
        #     data = dict ( res.json())
        request.env['payment.transaction'].sudo().form_feedback(post, 'boa')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/returnUrl3',
                type='http', auth='public', csrf=False, methods=['POST', 'GET'], save_session=False)
    def boa_request(self, **post):
        post.update({
            'tx_ref': self.tx_ref
        })
        _logger.info(
            'BOA: entering form_feedback from successful payment and returning(redirecting) ')
        request.env['payment.transaction'].sudo().form_feedback(post, 'boa')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/begin3', type='http', auth='public', csrf=False, methods=['POST'], website=True)
    def begin_transaction(self, **post):
        _logger.info(
            'BOA : Begining to parse data and post to request URL')
        request_url = 'https://api.chapa.co/v1/transaction/initialize'
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # self.private = post["private_key"]
        self.tx_ref = post['app_order_id']
        order_id = post['app_order_id']
        # if '-' in order_id:
        #     temp = order_id.split('-')
        #     order_id = temp[0][1:] + temp[1] + '_' + str(temp[0])[1:]
        # else:
        #     order_id = str(00) + '_' + order_id[1:]
        order_id =order_id + '__' + uuid.uuid1().hex
        req_data = {
            "phone": post["c_phone"],
            # "last": post["c_last_name"],
            # "email": post["c_email"],
            # "first": post["c_first_name"],
            "payer_id": post['boa_app_id'],
            "total": post["amount"],
            "stotal": post['amount'],
            "tx_ref": post['app_order_id'],
            "tax": 'pending',
            "shiping": 'no',

            # "callback_url" : str(urls.url_join(base_url, "/notifyUrl")),
            # "return_url": str(urls.url_join(base_url, "/returnUrl")),
        }
        first_data = {
            'trace_no': order_id,
            'amount': post["amount"],
            'phone': post["c_phone"],
            'appId': post['boa_app_id'],
        }
        try:
            response = requests.post(post['url'], json=first_data)


            if response.status_code >= 200 and response.status_code <= 300:
                _logger.info(
                    'BOA : Success in post request, set transaction to pending and redirect to new Transaction Url')
                response_json = response.json()
                post.update({
                    'tx_ref': post['app_order_id']
                })
                request.env['payment.transaction'].sudo().form_feedback(post, 'boa')
                return werkzeug.utils.redirect(response_json['result']["data"]["toPayUrl"])
            else:
                return http.request.render('boa_payment_acquirer.error')
                # raise werkzeug.exceptions.BadRequest(
                #     "Request not successful,Please check the keys or consult the admin.code-" + str(response.status_code))
                # return response.status_code

        except Exception as e:
            print(e)
            return http.request.render('boa_payment_acquirer.error')