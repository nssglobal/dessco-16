# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    pr_ref = fields.Char(string="PR ref")
    do_number=fields.Many2one('stock.picking',string="DO Number")
    do_date=fields.Datetime(related='do_number.scheduled_date')
    lpo_number=fields.Char(string="LPO Number")
    lpo_date=fields.Date('LPO Date')



