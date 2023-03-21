# -*- coding: utf-8 -*-


from odoo import models
from datetime import datetime
from pytz import timezone


class CustomReport(models.AbstractModel):
    _name = "report.de_user_ledger.de_partner_ledger_pdf_report"

    def get_user_debit(self, user):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        partner_ledger = sum(self.env['account.move.line'].search(
            [('move_id.user_id', '=', user.id), ('date', '>=', rec_model.start_date), ('date', '<=', rec_model.end_date),
             ('move_id.state', '=', 'posted'), ('account_id.account_type', '=', 'asset_receivable')], order="date asc").mapped('debit'))
        return partner_ledger

    def get_user_credit(self, user):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        partner_ledger = sum(self.env['account.move.line'].search(
            [('move_id.user_id', '=', user.id), ('date', '>=', rec_model.start_date), ('date', '<=', rec_model.end_date),
             ('move_id.state', '=', 'posted'), ('account_id.account_type', '=', 'asset_receivable')], order="date asc").mapped('credit'))
        return partner_ledger

    def get_opening_debit(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        open_bal = sum(self.env['account.move.line'].search(
            [('date', '<', rec_model.start_date),
             ('move_id.state', '=', 'posted'), ('account_id.account_type', '=', 'asset_receivable')]).mapped('debit'))
        # bal = 0
        # for rec in open_bal:
        #     bal = bal + rec.balance
        return open_bal

    def get_opening_credit(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        open_bal = sum(self.env['account.move.line'].search(
            [('date', '<', rec_model.start_date),
             ('move_id.state', '=', 'posted'), ('account_id.account_type', '=', 'asset_receivable')]).mapped('credit'))
        # bal = 0
        # for rec in open_bal:
        #     bal = bal + rec.balance
        return open_bal

    def get_print_date(self):
        now_utc_date = datetime.now()
        now_dubai = now_utc_date.astimezone(timezone('Asia/Karachi'))
        return now_dubai.strftime('%d/%m/%Y %H:%M:%S')

    def _get_report_values(self, docids, data=None):
        users = self.env['res.users'].browse(data['user_ids'])
        return {
            'doc_ids': self.ids,
            'doc_model': 'partner.ledger',
            'users': users,
            'print_date': self.get_print_date(),
            'login_user': self.env.user.name,

            'data': data,
            'get_user_debit': self.get_user_debit,
            'get_user_credit': self.get_user_credit,
            'get_opening_debit': self.get_opening_debit,
            'get_opening_credit': self.get_opening_credit,
        }
