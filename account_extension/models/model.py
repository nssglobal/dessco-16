# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    pr_ref = fields.Char(string="PR ref")
    do_numer=fields.Char(string="DO Number")
    lpo_numer=fields.Char(string="LPO Number")



