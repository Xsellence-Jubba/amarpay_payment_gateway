from odoo import models, fields, api, _


class AmarpayLog(models.Model):
    _name = 'amarpay.log'
    _description = 'Log'
    _order = 'id desc'

    text = fields.Text()
