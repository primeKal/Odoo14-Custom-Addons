from odoo.http import request
from odoo.exceptions import UserError
from werkzeug import urls

from odoo import http
import pprint
import time
import xmltodict
import requests

import logging

_logger = logging.getLogger(__name__)


class TelebirrUssdHandle(http.Controller):

    @http.route('/send_sms',
                type='json', auth='public', csrf=False, methods=['POST'], save_session=False)
    def send_sms(self, **kwargs):
        post = request.jsonrequest
        _logger.info(post)
        payerId = post['payer_id']
        appId = post['app_id']
        traceNo = post['trace_no']
        amount = post['amount']
        # issuedTo = post['phone']
        issuedTo = '0925499376'
        returnUrl = request.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/telebirr/ussd/callback'

        payer = request.env['aggrigator.payer'].sudo().search([('id', '=', payerId)]).sudo()

        if (not payer) or (not appId) or (not traceNo) or (not amount) :
            return 'missing data please configure'
        # everything seems to be ready so lets create the transaction
        transaction_data = {
            'payer': payer.id,
            'amount': amount,
            'trace_no': traceNo,
            'state': 'pending',
            'to': issuedTo
        }
        transaction = request.env['aggrigator.transaction'].sudo().create(transaction_data)
        if not transaction:
            return 'failed to create transaction'
        xmlData =  '''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:api="http://cps.huawei.com/cpsinterface/api_requestmgr" xmlns:req="http://cps.huawei.com/cpsinterface/request" xmlns:com="http://cps.huawei.com/cpsinterface/common">
   <soapenv:Header/>
   <soapenv:Body>
      <api:Request>
         <req:Header>
            <req:Version>1.0</req:Version>
            <req:CommandID>InitTrans_BuyGoodsForCustomer</req:CommandID>
            <req:OriginatorConversationID>{trace}</req:OriginatorConversationID>
            <req:Caller>
               <req:CallerType>2</req:CallerType>
               <req:ThirdPartyID>{caller}</req:ThirdPartyID>
               <req:Password>{pw}</req:Password>
               <req:ResultURL>{resultURL}</req:ResultURL>
            </req:Caller>
            <req:KeyOwner>1</req:KeyOwner>
            <req:Timestamp>{moment}</req:Timestamp>
         </req:Header>
         <req:Body>
            <req:Identity>
               <req:Initiator>
                  <req:IdentifierType>12</req:IdentifierType>
                  <req:Identifier>200001</req:Identifier>
                  <req:SecurityCredential>{Pin}</req:SecurityCredential>
                  <req:ShortCode>200001</req:ShortCode>
                  <!--<req:IdentifierType>12</req:IdentifierType>
                  <req:Identifier>1234567</req:Identifier>
                  <req:SecurityCredential>3iA2CDL1eHI=</req:SecurityCredential>
                  <req:ShortCode>90000001</req:ShortCode>-->
               </req:Initiator>
               <req:PrimaryParty>
                  <req:IdentifierType>1</req:IdentifierType>
                  <req:Identifier>{phone}</req:Identifier>
               </req:PrimaryParty>
               <req:ReceiverParty>
                  <req:IdentifierType>4</req:IdentifierType>
                  <req:Identifier>{shortcode}</req:Identifier>
               </req:ReceiverParty>
            </req:Identity>
            <req:TransactionRequest>
               <req:Parameters>
                  <req:Amount>{amount}</req:Amount>
                  <req:Currency>ETB</req:Currency>
               </req:Parameters>
            </req:TransactionRequest>
         </req:Body>
      </api:Request>
   </soapenv:Body>
</soapenv:Envelope>'''.format(trace=traceNo, caller=payer.callerId,
                               pw=payer.callerEncryptedPassword,resultURL=returnUrl,
                               moment=time.time(),Pin=payer.callerPin,phone=issuedTo,
                               shortcode=payer.shortCode,amount=amount)




            # .format({'trace':traceNo, 'caller':payer.callerId,
            #                    'pw':payer.callerEncryptedPassword,'resultURL':returnUrl,
            #                    'moment':time.time(),'Pin':payer.callerPin,'phone':issuedTo,
            #                    'shortcode':payer.shortCode,'amount':amount})
        _logger.info(xmlData)
        header =  { "Content-Type": "text/xml" }
        response = requests.post(payer.url, headers=header, data=xmlData)
        _logger.info(response)
        if response.data :
            my_dict = xmltodict.parse(response.data)
            if ( my_dict["soapenv:Envelope"]["soapenv:Body"][0]["api:Response"][0]["res:Body"][0]["res:ResponseCode"] == 0):
                return 'USSD Sent Successfully'
            else :
                return 'error occured here'


    @http.route('/callback',
                type='http', auth='public', csrf=False, methods=['POST'], save_session=False)
    def callback(self, **post):
        _logger.info(post)
        body = post['body']
        data = xmltodict.parse(body)
        _logger.info(data)
        resultCode = data["soapenv:Envelope"]["soapenv:Body"][0]["api:Result"][0]["res:Body"][0]["res:ResultCode"][0];
        resultDesc = data["soapenv:Envelope"]["soapenv:Body"][0]["api:Result"][0]["res:Body"][0]["res:ResultDesc"][0];
        trace_no = data["soapenv:Envelope"]["soapenv:Body"][0]["api:Result"][0]["res:Body"][0]["res:TransactionResult"][0][
            "res:TransactionID"][0];
        _logger.info(trace_no)
        transaction = request.env['aggrigator.transaction'].search([('traceNo', '=', trace_no)])
        if transaction:
            res = {
                'state': 'confiremed'
            }
            transaction.write(res)
            # here we will send confiramtion request to our saved return url


