from datetime import datetime
import werkzeug
from odoo import http
from odoo.http import request
import requests

import base64
import hmac
import hashlib

import uuid
import logging

_logger = logging.getLogger(__name__)


class ZemenPaymentHandler(http.Controller):

    @http.route('/boa/process',
                type='json', auth='public', csrf=False, methods=['POST'], save_session=False)
    def boa_process(self, **kwargs):
        post = request.jsonrequest
        first_name = post['first']
        last_name = post['last']
        email = post['email']
        phone = post['phone']
        stotal = post['stotal']
        total = post['total']
        tax = post['tax']
        shiping = post['shiping']
        order_id = post['order_id']
        payer = post['payer_id']
        today = datetime.now()
        iso_date = today.isoformat()
        dd = iso_date.split('.')
        datee = dd[0] + 'z'
        _logger.info(datee)
        rn = uuid.uuid1()
        tr = order_id
        payer_model = request.env['aggrigator.payer'].sudo() \
            .search([('id', '=', payer)])
        if not payer_model :
            return {'error': True}
        data = {
            "access_key": payer_model.access_key,
            "profile_id": payer_model.profile_id,
            "transaction_uuid": tr,
            "signed_field_names":
                "access_key,profile_id,transaction_uuid,signed_field_names,unsigned_field_names,signed_date_time,locale,transaction_type,reference_number,amount,currency",
            "unsigned_field_names": "",
            "signed_date_time": datee,
            "locale": "en",
            "transaction_type": "sale",
            "reference_number": rn,
            "amount": total,
            "currency": "ETB"
        }
        data2 = {
            {"name": "access_key", "value": payer_model.access_key},
            {"name": "profile_id", "value": payer_model.profile_id},
            {"name": "transaction_uuid", "value": tr},
            {"name": "signed_field_names",
             "value": "access_key,profile_id,transaction_uuid,signed_field_names,unsigned_field_names,signed_date_time,locale,transaction_type,reference_number,amount,currency"},
            {"name": "unsigned_field_names", "value": ""},
            {"name": "signed_date_time", "value": datee},
            {"name": "locale", "value": "en"},
            {"name": "transaction_type", "value": "sale"},
            {"name": "reference_number", "value": rn},
            {"name": "amount", "value": total},
            {"name": "currency", "value": "ETB"},
        }
        data2.add({
            "name": "signature", "value": self.signData(data, data.signed_field_names, payer_model.secret_key)
        })
        data3 = [
            {"name": "bill_to_forename", "value": first_name, "label": "First Name"},
            {"name": "bill_to_surname", "value": last_name, "label": "Last Name"},
            {"name": "bill_to_email", "value": email, "label": "Email"},
            {"name": "bill_to_phone", "value": phone, "label": "Phone"},
        ]
        tran = request.env['aggrigator.payer'].create({
            'payer': payer_model.id,
            'amount': total,
            'trace_no': tr,
            'state': 'pending',
            'to': phone,
        })
        if not tran:
            return 'error occured'
        return http.request.render('payment_aggri.boa', {
            "data": data2,
            "total": "$" + total,
            "orderId": "" + order_id,
            'subtotal': "$" + stotal,
            "tax": "$" + tax,
            "shiping": "$" + shiping,
            "data3": data3,
            "url": payer_model.url
        })

    def signData(self, data, signed, secret):
        d = []
        fields = signed.split(',')
        for field in fields:
            d.append(field + "=" + data[field])
        data = ",".join(d)
        _logger.info(data)
        hash = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        _logger.info(self.isBase64(hash))
        return hash

    def isBase64(s):
        try:
            return base64.b64encode(base64.b64decode(s)) == s
        except Exception:
            return False

    @http.route('/boa/callback',
                type='json', auth='public', csrf=False, methods=['POST'], save_session=False)
    def boa_process(self, **kwargs):
        post = request.jsonrequest
        res_data = {
            'req_card_number': post['req_card_number'],
            'reason_code': post['reason_code'],
            'payer_authentication_reason_code': post['payer_authentication_reason_code'],
            'req_currency': post['req_currency'],
            'req_amount': post['req_amount'],
            'decision': post['decision'],
            'message': post['message'],
            'req_reference_number': post['req_reference_number'],
            'req_transaction_uuid': post['req_transaction_uuid']
        }
        tran = request.env['aggrigator.transaction'].search([('trace_no', '=', post['req_transaction_uuid'])])
        if tran:
            # here we will send callback to application
            print('sending')
