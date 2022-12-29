# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    scope_of_work = fields.Text(string="Scope of Work")
    inclusion = fields.Text(string="Inclusion")
    exclusion = fields.Text(string="Exclusion")


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    scope_of_work = fields.Text(string="Scope of Work")
    inclusion = fields.Text(string="Inclusion")
    exclusion = fields.Text(string="Exclusion")
    transporter = fields.Many2one("res.partner",string="Transporter")



