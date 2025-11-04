# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID
from odoo.http import request as req
import requests
import json
from werkzeug.utils import redirect


class Amarpay(http.Controller):
    @http.route('/t55', auth='public')
    def t55(self, **kw):
        order = req.env['sale.order'].sudo().search([('id', '=', 32)])
        if not order:
            return 'No order found'

        payment_url = req.env['amarpay.transaction'].sudo().get_payment_url(order)
        if payment_url:
            return redirect(payment_url)
        return "t55"

    @http.route('/t66', auth='public')
    def t66(self, **kw):
        print('kw', kw)
        return "t66"

    # @http.route('/payment/ipn', type='http', auth='none', methods=['POST'], csrf=False, save_session=False)
    @http.route('/t77', type='http', auth='none')
    def t77(self, **kw):

        # print(' ------------- ipn  ------')
        # print(f' kw  -- {kw}')
        #
        # tran_id = kw.get('tran_id')
        # status = kw.get('status')
        # val_id = kw.get('val_id')
        # amount = kw.get('amount')
        # currency = kw.get('currency')

        # Test
        tran_id = '111'
        amount = '100.00'
        status = 'VALID'
        val_id = '111'

        a = req.env['amarpay.transaction'].with_user(SUPERUSER_ID).invoice_generation(tran_id,amount,status,val_id)
        print('a', a)
        # return {"status": "received"}

        return 't77'

    @http.route('/payment/success/process', type='http', auth='none', methods=['POST'], csrf=False, save_session=False)
    def payment_success_process(self, **kw):
        log_str = str(kw)
        req.env['amarpay.log'].create({'text': log_str})
        return 't77'
