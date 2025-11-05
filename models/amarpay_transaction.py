from odoo import models, fields, api, _, SUPERUSER_ID
import requests
import json


class AmarpayTransaction(models.Model):
    _name = 'amarpay.transaction'
    _description = 'Transaction'

    amount_total = fields.Float()
    currency = fields.Char(string="Currency")
    tran_id = fields.Char(string="Transaction ID")
    status = fields.Char(string='Status')
    val_id = fields.Char(string='Val ID')

    order_id = fields.Many2one('sale.order', string="Order")
    partner_id = fields.Many2one('res.partner', string="Customer")

    multi_card_name = fields.Char(string="Multi Card Name")
    value_a = fields.Char(string="Value A")
    value_b = fields.Char(string="Value B")
    value_c = fields.Char(string="Value C")
    value_d = fields.Char(string="Value D")

    def get_payment_url(self, order):

        setting = self.env['amarpay.setting'].search([], limit=1)
        if not setting:
            return False

        if not setting.mode:
            return False

        url = ''
        if setting.mode == 'test':
            url = setting.sandbox_url
        else:
            url = setting.url

        payload = json.dumps({
            "order_id": order.id,
            "store_id": setting.store_id,
            "tran_id": order.name,
            "success_url": setting.success_url,
            "fail_url": setting.fail_url,
            "cancel_url": setting.cancel_url,
            "amount": order.amount_total,
            "currency": order.currency_id.name or 'BDT',
            "signature_key": setting.signature_key,
            "desc": order.name,
            "cus_name": order.partner_id.name,
            "cus_email": order.partner_id.email or 'test@example.invalid',
            "cus_add1": order.partner_id.street,
            "cus_add2": order.partner_id.street,
            "cus_city": order.partner_id.city,
            "cus_state": order.partner_id.city,
            "cus_postcode": order.partner_id.zip,
            "cus_country": order.partner_id.country_id.name if order.partner_id.country_id else "",
            "cus_phone": order.partner_id.mobile,
            "type": "json"
        })
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
            try:
                dic_res = response.json()
                print('dic_res', dic_res)
                if dic_res.get('result') == 'true' and dic_res.get('payment_url'):
                    return dic_res.get('payment_url')
                else:
                    return None
            except json.JSONDecodeError:
                return None
        else:
            return None

    @api.model
    def invoice_generation(self, tran_id, amount, status=False, val_id=False):
        try:
            # print(f"--------------------------------------------------- invoice_generation -------------------------------------------------------------")
            self = self.with_user(SUPERUSER_ID)
            # 1. Find the transaction and validate it
            transaction = self.search([('tran_id', '=', tran_id)], limit=1)

            if not transaction or float(transaction.amount_total) != float(amount):
                return {"status": "failed", "message": "Transaction not found or amount mismatch."}

            # 2. Update transaction fields and check payment status
            transaction.write({"status": status, "val_id": val_id})

            if status != "VALID":
                return {"status": "failed", "message": f"Payment status is {status}"}

            order = transaction.order_id
            if not order:
                return {"status": "failed", "message": "No linked Sale Order"}

            # 3. Confirm the sale order (this also creates the invoice)
            if order.state in ['draft', 'sent']:
                order.action_confirm()

            invoices = order._create_invoices()

            # 4. Find the created invoice(s)
            invoices = order.invoice_ids.filtered(lambda inv: inv.state == 'draft')
            if not invoices:
                return {"status": "failed", "message": "No draft invoices to post."}

            # 5. Post the invoice(s)
            invoices.action_post()

            # 6. Register the payment using the standard Odoo wizard
            # The wizard handles the account assignment and reconciliation automatically.
            payment_register = self.env['account.payment.register'].sudo().with_context(
                active_model='account.move',
                active_ids=invoices.ids,
            )

            payment_vals = payment_register.default_get(payment_register.fields_get())

            # Override the journal to use your SSLCommerz account
            # First, find the journal associated with your SSLCommerz account
            amarpay_journal = self.env['account.journal'].sudo().search([
                ('name', 'ilike', 'AMARPAY'),
            ], limit=1)

            if amarpay_journal:
                payment_vals['journal_id'] = amarpay_journal.id
            else:
                return {"status": "failed", "message": "AMARPAY journal not found."}

            payment = payment_register.create(payment_vals)
            payment.action_create_payments()

            return {
                "status": True,
                "sale_order_id": order.id,
                "invoice_ids": invoices.ids,
                "message": "The order has been confirmed successfully."
            }
        except Exception as e:
            return {"status": False, "error": str(e)}
