# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    pr_ref = fields.Char(string="PR ref")
    do_number=fields.Char(string="DO Number",compute="compute_delivery_order")
    lpo_number=fields.Char(string="LPO Number")
    do_date=fields.Datetime(string="LPO Number")
    lpo_date=fields.Date(string="LPO Number")

    def compute_delivery_order(self):
        for i in self:
            do_obj=self.env['stock.picking'].search([("origin",'=',i.invoice_origin),("state",'=','done')],limit=1)
            i.do_number= do_obj.name
            i.do_date= do_obj.scheduled_date


