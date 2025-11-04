from odoo import models, fields, api, _


class AmarpayLog(models.Model):
    _name = 'amarpay.log'
    _description = 'Log'

    text = fields.Text()
