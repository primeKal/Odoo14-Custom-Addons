import json
from urllib.parse import urlencode,parse_qs



import werkzeug
from odoo import http
from odoo.http import request
import  requests

import uuid
import logging

_logger = logging.getLogger(__name__)


class ZemenPaymentHandler(http.Controller):

    @http.route('/zemen/postbill',
                type='json', auth='public', csrf=False, methods=['POST'], save_session=False)
    def zemen_post_bill(self, **kwargs):
        post = request.jsonrequest
        _logger.info(post)
        payerId = post['payer_id']
        traceNo = post['trace_no']
        amount = post['amount']
        issuedTo = post['phone']
        returnUrl = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/telebirr/ussd/callback'
        session = uuid.uuid1()
        payer = request.env['aggrigator.payer'].sudo().search([('id', '=', payerId)]).sudo()

        if (not payer)  or (not traceNo) or (not amount):
            return 'missing data please configure'
        # everything seems to be ready so lets create the transaction
        transaction_data = {
            'payer': payer.id,
            'amount': amount,
            'trace_no': traceNo,
            'state': 'pending',
            'to': issuedTo,
            'session': session
        }
        transaction = request.env['aggrigator.transaction'].sudo().create(transaction_data)
        if transaction:
            return {'message': "Invoice added successfully",
                    'success': True,
                    'data': {
                        'toPayUrl': request.env['ir.config_parameter'].sudo().get_param(
                            'web.base.url') + "/zemen/processPayment/" + transaction.session
                        }
                    }
        else:
            return 'Error occured'

    @http.route('/zemen/customer/<session>',
                type='http', auth='public', csrf=False, methods=['GET'], save_session=False)
    def customer_confirem(self, session, **kwargs):
        tran = request.env['aggrigator.transaction'].sudo().search([('session', '=', session)]).sudo()
        if tran:
            tran.state = 'confiremed'
            _logger.info(tran.success_indicator)
            _logger.info(str(kwargs['resultIndicator']))
            if tran.success_indicator == str(kwargs['resultIndicator']) :
                redirect = tran.payer.callback
                if redirect:
                    contents = {
                        'success': True,
                        'trace_no': tran.trace_no,
                        'successIndicator': tran.success_indicator
                    }
                    if tran.payer.callback_type == 'redirect':
                        return werkzeug.utils.redirect(redirect + '/True')
                    else:
                        request_headers = {
                            # "Authorization" : "Bearer " + post["private_key"],
                            "Content-Type": "application/json",
                        }
                        response = requests.post(redirect, headers=request_headers, json=contents)
                        return True
                else:
                    return'no callback, but payment success'
            else:
                redirect = tran.payer.callback
                if redirect:
                    contents = {
                        'success': False,
                        'trace_no': tran.trace_no,
                        'successIndicator': tran.success_indicator
                    }
                    if tran.payer.callback_type == 'redirect':
                        return werkzeug.utils.redirect(redirect + '/True')
                    else:
                        request_headers = {
                            # "Authorization" : "Bearer " + post["private_key"],
                            "Content-Type": "application/json",
                        }
                        response = requests.post(redirect, headers=request_headers, json=contents)
                        return True
                else:
                    return'no callback, but payment success'
                return 'errorrr'
            # here we will send a url to confirem purchase to tran.payer.returnurl


    @http.route('/zemen/processPayment/<session>',
                type='http', auth='public', csrf=False, methods=['POST','GET'], save_session=False)
    def processing_payment(self, session):
        _logger.info('here to process your payments ')
        _logger.info(session)
        tran = request.env['aggrigator.transaction'].sudo().search([('session', '=', session)]).sudo()
        if not tran:
            return 'error: could not find your data'
        sessionData = self.getSessionData(tran.trace_no,tran.amount,tran.session,tran)
        # i dont know what to do from here my mannnnnnn
        return http.request.render('payment_aggri.zemen', {
            "data": {
                'id' : sessionData['sessionId'],
                'name': tran.payer.who.display_name,
                'js_url' :tran.payer.js_url
            },
        })
    # to check if the template worksss
    @http.route('/zemen/test',
                type='http', auth='public', csrf=False, methods=['GET'], save_session=False)
    def tes(self):
        return http.request.render('payment_aggri.zemen')

    def getSessionData(self,trace_no, amount, session,transaction):
        return_url =request.env['ir.config_parameter'].sudo().get_param(
                            'web.base.url') + "/zemen/customer/" + session
        data_before = {
            # 'apiOperation':'CREATE_CHECKOUT_SESSION',
            # "interaction.operation": "AUTHORIZE",
            'apiOperation': "INITIATE_CHECKOUT",
            "interaction.operation": "PURCHASE",
            'merchant': transaction.payer.merchant,
            'apiUsername': transaction.payer.apiUsername,
            'apiPassword': transaction.payer.apiPassword,
            "order.id": trace_no,
            "order.amount": amount,
            "order.description": "Payment for ETTA",
            "order.currency": "ETB",
            "interaction.returnUrl": str(return_url),
            "interaction.merchant.name": transaction.payer.who.display_name
        }
        _logger.info(data_before)
        data = urlencode(data_before)
        _logger.info(data)

        header =  { "Content-Type": "application/x-www-form-urlencoded" }
        response = requests.post(transaction.payer.url, headers=header, data=data)
        resp = response.content
        _logger.info(resp)
        # resp = b'checkoutMode=WEBSITE&merchant=000000001255&result=SUCCESS&session.id=SESSION0002073125537K8363263I53&session.updateStatus=SUCCESS&session.version=004a181401&successIndicator=05b5a3dd1aef40fe'
        if resp:
            # resp = str(resp)
            resp = parse_qs(resp)
            # sessionId =  resp.split("session.id=")[1].split("&")[0]
            # successIndicator = resp.split("successIndicator=")[1].split("&")[0]
            sessionId = resp[b'session.id'][0]
            sessionId = sessionId.decode('utf-8')
            successIndicator = resp[b'successIndicator'][0]
            successIndicator = successIndicator.decode('utf-8')
            transaction.success_indicator = successIndicator
            return { 'sessionId':sessionId,'successIndicator':successIndicator}


