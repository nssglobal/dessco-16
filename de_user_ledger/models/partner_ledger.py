
import time

from odoo import fields,api,models
from dateutil import parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class PartnerLedger(models.TransientModel):
    _name = 'partner.ledger'

    start_date = fields.Date(string='From Date', required=True, default=fields.Date.today().replace(day=1))
    end_date = fields.Date(string='To Date', required=True, default=fields.Date.today())
    user_ids = fields.Many2many('res.users', string='User', required=True, help='Select Users for movement')

    def print_report(self):
        data = {'user_ids': self.user_ids.ids, 'start_date': self.start_date, 'end_date': self.end_date}
        return self.env.ref('de_user_ledger.partner_ledger_pdf').report_action(self, data)


# class ResPartner(models.Model):
#     _inherit = 'res.partner'
#
#     def action_partner_ledger(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Partner Ledger',
#             'view_id': self.env.ref('de_user_ledger.partner_ledger_wizard_report', False).id,
#             'target': 'new',
#             'res_model': 'partner.ledger',
#             'context': {'default_partner_id': self.id},
#             'view_mode': 'form',
#         }





