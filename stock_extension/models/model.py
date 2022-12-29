# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_person = fields.Char("Delivery Person")
    delivery_person_mobile = fields.Char("Delivery Person's Contact")
    so_id = fields.Many2one('sale.order',string="Sale Order",compute="compute_the_sale_order_no")


    def compute_the_sale_order_no(self):
        for rec in self:
            sale_id = self.env['sale.order'].search([('name', '=', rec.origin)], limit=1)
            rec.so_id=sale_id.id




