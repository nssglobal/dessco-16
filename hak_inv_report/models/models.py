# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    def get_amount_in_word(self):
        text = self.currency_id.amount_to_text(self.amount_total)
        return text.title()
