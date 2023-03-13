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


class HelloCash(http.Controller):

    @http.route('/send_invoice',
                type='json', auth='public', csrf=False, methods=['POST'], save_session=False)
    def send_helocash_invoice(self, **kwargs):
        post = request.jsonrequest
        amount = post['amount']
        description = post['description']
        # we need to format the code hererererererere
        issued_to = post['phone']
        if post['trace_no']:
            trace_no = post['trace_no']
        else:
            trace_no = uuid.uuid1()
        payerId = post['payer_id']
        payer_model = request.env['aggrigator.payer'].sudo() \
            .search([('id', '=', payerId)])

        self.sendInvoice(amount,description,issued_to,trace_no,payer_model)




    def sendInvoice(self,amount,description,issued_to,trace_no,payer):
        hellocash_token = self.getHeloCashToken(payer)
        amount = round(amount, 1)
        # to be cintinuedddd



    def getHeloCashToken(self,payer):
        json_data = {
            "principal": payer.hello_username,
            "credentials": payer.hello_password,
            "system": payer.hello_system
        }
        response = requests.post(payer.url + 'authenticate', json=json_data)
        _logger.info(response)
        return response.json()['token']
