# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_person = fields.Char("Delivery Person")
    delivery_person_mobile = fields.Char("Delivery Person's Contact")

    def do_print_delivery_order(self):
        if self.picking_type_id.code == 'outgoing' and self.state == 'done':
            sale_order = self.group_id
            so_obj = self.env['sale.order']
            sale_id = so_obj.search([('id','=',sale_order.id)], limit=1)
            if sale_id:
                return self.env.ref('stock_extension.action_report_deliveryslip').report_action(self)
            else:
                raise ValidationError("Sale Order doesnt exist !!")
            
        else:
            raise ValidationError("This record is not a Validated Delivery Order")


    def get_sale_order_data(self):
        for rec in self:
            sale_order = rec.group_id
            print(sale_order)
            so_obj = self.env['sale.order']
            if sale_order:
                sale_id = so_obj.search([('id', '=', sale_order.id)], limit=1)
                if sale_id:
                    return sale_id
                else:
                    raise ValidationError("Sale Order doesnt exist !!")



