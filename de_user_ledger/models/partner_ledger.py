
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


class CustomerLedger(models.TransientModel):
    _name = 'customer.ledger'

    start_date = fields.Date(string='From Date', required=True, default=fields.Date.today().replace(day=1))
    end_date = fields.Date(string='To Date', required=True, default=fields.Date.today())
    user_ids = fields.Many2many('res.users', string='User', required=True, help='Select Users for movement')

    def print_report(self):
        data = {'user_ids': self.user_ids.ids, 'start_date': self.start_date, 'end_date': self.end_date}
        return self.env.ref('de_user_ledger.customer_ledger_pdf').report_action(self, data)


class LedgerReport(models.TransientModel):
    _name = 'ledger.report'

    start_date = fields.Date(string='From Date', required=True, default=fields.Date.today().replace(day=1))
    end_date = fields.Date(string='To Date', required=True, default=fields.Date.today())
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, help='Select Partner for movement')

    def print_report(self):
        data = {'user_ids': self.partner_id.id, 'start_date': self.start_date, 'end_date': self.end_date}
        return self.env.ref('de_user_ledger.action_ledger_pdf').report_action(self, data)


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    def get_overdue_days(self):
        days = (datetime.today().date() - self.invoice_date_due).days
        return days



