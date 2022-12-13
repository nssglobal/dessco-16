# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
# from odoo.tools.translate import TranslationImporter


class SaleOrder(models.Model):
    _inherit = "sale.order"

    po_ref = fields.Char(string="PO ref")



