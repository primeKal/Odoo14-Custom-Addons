from datetime import datetime
import werkzeug
from odoo import http
from odoo.http import request
import requests
import json
import base64
import hmac
import hashlib

import uuid
import logging

_logger = logging.getLogger(__name__)


class ZemenPaymentHandler(http.Controller):

    @http.route('/send_otp',
                type='json', auth='public', csrf=False, methods=['POST'], save_session=False)
    def amole_send_otp(self, **kwargs):
        post = request.jsonrequest
        # we will need to format the phone numebr
        phone = '+2519' + post['phone']
        desc = post['description']
        payerId = post['payer_id']
        payer_model = request.env['aggrigator.payer'].sudo() \
            .search([('id', '=', payerId)])
        return self.request_otp(phone, desc, payer_model)

    def request_otp(self, phone, desc, payer):
        uuid_trace_no = uuid.uuid1()
        form = {
            "BODY_CardNumber": phone,
            "BODY_PaymentAction": "09",
            "FettanMerchantId": payer.fetan_meerchant_id,
            "BODY_OrderDescription": desc,
            "BODY_SourceTransID": uuid_trace_no,
        }
        header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "HDR_Signature": payer.hdr_signiture,
            "HDR_IPAddress": payer.hrd_ipaddress,
            "HDR_UserName": payer.hdr_username,
            "HDR_Password": payer.hrd_password,
        }
        response = requests.post(payer.url, headers=header, data=form)
        _logger.info(response)

        json_data = json.loads(response.text)
        if json_data[0].MSG_ErrorCode == 0o00001:
            return {
                'msg': 'Successfully Completed !',
                'shortMsg': json_data[0].MSG_ShortMessage,
                'longMsg': json_data[0].MSG_LongMessage
            }
        else:
            return {
                'msg': 'failed!',
                'shortMsg': json_data[0].MSG_ShortMessage,
                'longMsg': json_data[0].MSG_LongMessage
            }
    @http.route('/pay',
                type='json', auth='public', csrf=False, methods=['POST'], save_session=False)
    def amole_send_otp(self, **kwargs):
        post = request.jsonrequest
        # we need to format this phone
        phone = post['phone']
        code = post['code']
        amount = post['amount']
        desc = post['description']
        if post['trace_no']:
            trace_no = post['trace_no']
        else :
            trace_no = uuid.uuid1()
        payerId = post['payer_id']
        payer_model = request.env['aggrigator.payer'].sudo() \
            .search([('id', '=', payerId)])
        response = self.pay(phone,code,amount,desc,trace_no,payer_model)
        if response.MSG_ErrorCode == 0o00001:
            tran = request.env['aggrigator.payer'].create({
                'payer': payer_model.id,
                'amount': amount,
                'trace_no': trace_no,
                'state': 'confiremed',
                'to': phone,
                'amole_code': code
            })
            if not tran:
                return 'error occured'
            return {
                'msg': "Successfully Completed !",
                'shortMsg': response.MSG_ShortMessage,
                'longMsg': response.MSG_LongMessage
            }
        else :
            tran = request.env['aggrigator.payer'].create({
                'payer': payer_model.id,
                'amount': amount,
                'trace_no': trace_no,
                'state': 'failed',
                'to': phone,
                'amole_code': code + response.MSG_ShortMessage
            })
            if not tran:
                return 'error occured while creating the transaction'
            return {
                'msg': "FAILED",
                'shortMsg': response.MSG_ShortMessage,
                'longMsg': response.MSG_LongMessage
            }
    def pay(self,phone,code,amount,desc, trace_no,payer):
        form = {
            "BODY_CardNumber":phone,
            "BODY_PaymentAction": "01",
            # "FettanMerchantID": payer.fetan_meerchant_id,
            "BODY_AmoleMerchantID": payer.fetan_meerchant_id,
            "BODY_OrderDescription": desc,
            "BODY_PIN": code,
            "BODY_AmountX": amount,
            "BODY_SourceTransID": trace_no,
        }
        header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "HDR_Signatur": payer.hdr_signiture,
            "HDR_IPAddress": payer.hrd_ipaddress,
            "HDR_UserName": payer.hdr_username,
            "HDR_Password": payer.hrd_password,
        }
        response = requests.post(payer.url, headers=header, data=form)
        _logger.info(response)
        json_data = json.loads(response.text)
        return json_data[0]


