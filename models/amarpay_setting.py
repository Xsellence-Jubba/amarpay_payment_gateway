from odoo import models, fields, api, _


class AmarpaySetting(models.Model):
    _name = 'amarpay.setting'
    _description = 'Setting'

    sandbox_url = fields.Char(required=True)
    url = fields.Char(required=True)
    mode = fields.Selection([
        ('test', 'Test'),
        ('production', 'Production'),
    ])

    store_id = fields.Char(required=True)
    tran_id = fields.Char()
    success_url = fields.Char(required=True)
    fail_url = fields.Char(required=True)
    cancel_url = fields.Char(required=True)
    currency = fields.Char()
    signature_key = fields.Char()
