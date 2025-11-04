# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID
from odoo.http import request as req
import requests
import json
from werkzeug.utils import redirect


class Amarpay(http.Controller):
    @http.route('/payment/success/process', type='http', auth='public', methods=['POST'], csrf=False,
                save_session=False)
    def payment_success_process(self, **kw):
        sample = {
            "pg_service_charge_bdt": "2.10",
            "amount_original": "100.00",
            "gateway_fee": "",
            "pg_service_charge_usd": "Not-Available",
            "pg_card_bank_name": "Not Available",
            "pg_card_bank_country": "Not Available",
            "card_number": "1234XXXXXXXXX123",
            "card_holder": "",
            "status_code": "2",
            "pay_status": "Successful",
            "success_url": "https://new.jubbaa.com/payment/success/process",
            "fail_url": "https://new.jubbaa.com/payment/fail",
            "cus_name": "Abdur Razzak 2",
            "cus_email": "razzak606@gmail.com",
            "cus_phone": "+8801731001895",
            "currency_merchant": "BDT",
            "convertion_rate": "",
            "ip_address": "43.230.121.46",
            "other_currency": "100.00",
            "amount_currency": "100.00",
            "pg_txnid": "AAM1762248841217021",
            "epw_txnid": "AAM1762248841217021",
            "mer_txnid": "1231231737",
            "store_id": "aamarpaytest",
            "merchant_id": "aamarpaytest",
            "currency": "BDT",
            "store_amount": "97.90",
            "pay_time": "2025-11-04 15:34:20",
            "amount": "100.00",
            "bank_txn": "1100556154788",
            "card_type": "bKash-bKash",
            "reason": "Not Available",
            "pg_card_risklevel": "0",
            "pg_error_code_details": "Not Available",
            "opt_a": "",
            "opt_b": "",
            "opt_c": "",
            "opt_d": "",
        }

        log_str = str(kw)
        req.env['amarpay.log'].create({'text': log_str})

        # Create transaction
        tran_id = kw.get('pg_txnid')
        amount = kw.get('amount')
        status = 'VALID'
        val_id = kw.get('pg_txnid')

        if not tran_id:
            return 'Trand id not found'

        new_tran = req.env['amarpay.transaction'].create({
            'amount_total': amount,
            'currency': 'BDT',
            'tran_id': tran_id,
            'val_id': val_id,
            'status': status,
            'order_id': 64, # change
            'partner_id': 32, # change
        })

        tran = req.env['amarpay.transaction'].with_user(SUPERUSER_ID).invoice_generation(tran_id,amount,status,val_id)
        print('tran', tran)
        # return {"status": "received"}

        if not tran:
            return 'tran return empty'

        if tran.get('status'):
            req.redirect('/payment/success')

        # if fail
        return '/payment/success/process'

    @http.route('/payment/success', type='http', auth='public')
    def payment_success(self, **kw):
        return 'payment_success'
