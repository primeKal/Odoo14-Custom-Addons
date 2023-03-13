from odoo import fields, models, api, registry, sql_db
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

class ExtendedHrContract(models.Model):
    _inherit = 'purchase.requisition'

    def analyze(self):
        print('sdkjsdjkfhsdjkf')
        _logger.info('about to find these shits')
        tender_products = self.line_ids
        tender_rfq = self.env['purchase.order'].search([('requisition_id','=',self.id)])
        _logger.info(tender_products)
        _logger.info(tender_rfq)
        if len(tender_products) == 0:
            _logger.info('thank god no products in the tender/or we can raise an error')
        if len(tender_rfq) == 0 :
            _logger.info('thank god No rfq detected /or we can raise an error')
        # for each tender lets find the minumemu price
        for tender in tender_products:
            data = self.findCheapest(tender,tender_rfq)
            _logger.info(data)
            # lets remove the reset product from the tendet lines
            self.remove_line_from_all_except_one(data['product_line'].product_id,data['product_line'],tender_rfq)

            # for rfq in tender_rfq:
            #     rfq_line = rfq.order_line
            #     for product in rfq_line:
            #         if tender.product_id == product.product_id:
            #             #  matchinggggg  price found
            #             print('asdfghj')
        

    def findCheapest(self, product_id,rfqs):
        _logger.info('starting to find the cheapest product')
        _logger.info(product_id)
        found = 0
        prod = None
        rfq_product = None
        for rfq in rfqs:
            _logger.info(rfq)
            _logger.info('^^^^^^^ current rfq')
            for product in rfq.order_line:
                _logger.info(product)
                _logger.info('product in rfq')
                if product_id.product_id == product.product_id:
                    _logger.info('found the matchng producttt')
                    _logger.info(product_id)
                    _logger.info(product.price_unit)
                    if found == 0 or found>product.price_unit:
                        _logger.info('found the lower price toooo')
                        found = product.price_unit
                        prod = product
                        rfq_product = rfq
        return {
            'product_line': prod,
            'rfq': rfq_product,
            'found': found
        }
    def remove_line_from_all_except_one(self, product_id,linee,rfqs):
        _logger.info('hiiiiiiiiiiiiiii')
        _logger.info('we will remove all rfqss product_id except rfq')
        for rffqqq in rfqs:
            _logger.info(rffqqq.name)
            for line in rffqqq.order_line:
                if linee == line:
                    _logger.info('skipping this')
                    break
                if product_id == line.product_id:
                    _logger.info('this is to be removed')
                    _logger.info('remove this line from the order line......')
                    rffqqq.write({
                        'order_line' : [(3,line.id)]
                    })