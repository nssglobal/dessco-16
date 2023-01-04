# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    do_number=fields.Char(string="DO Number",compute="compute_delivery_order")
    
    do_date=fields.Datetime(string="DO Date")
    lpo_number=fields.Char(string="LPO Number")
    lpo_date=fields.Date(string="LPO Date")
    scope_of_work = fields.Text(string="Scope of Work")

    def compute_delivery_order(self):
        for i in self:
            do_obj=self.env['stock.picking'].search([("origin",'=',i.invoice_origin),("state",'=','done')],limit=1)
            i.do_number= do_obj.name
            i.do_date= do_obj.scheduled_date
            i.scope_of_work=do_obj.so_id.scope_of_work


