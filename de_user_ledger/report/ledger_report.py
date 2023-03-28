# -*- coding: utf-8 -*-


from odoo import models
from datetime import datetime
from pytz import timezone


class CustomerReport(models.AbstractModel):
    _name = "report.de_user_ledger.ledger_pdf_report"

    # def get_user_debit(self, user):
        # model = self.env.context.get('active_model')
        # rec_model = self.env[model].browse(self.env.context.get('active_id'))
        # partner_ledger = sum(self.env['account.move.line'].search(
        #     [('move_id.user_id', '=', user.id), ('date', '>=', rec_model.start_date), ('date', '<=', rec_model.end_date),
        #      ('move_id.state', '=', 'posted'), ('account_id.account_type', '=', 'asset_receivable')], order="date asc").mapped('debit'))
        # return partner_ledger

    def get_partner_ledger(self):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        invoices = self.env['account.move'].search(
            [('move_type', '=', 'out_invoice'),('partner_id', '=', rec_model.partner_id.id), ('invoice_date', '>=', rec_model.start_date), ('invoice_date', '<=', rec_model.end_date),
             ('state', '=', 'posted')], order="invoice_date asc")
        return invoices

    # def get_users_customer(self, user):
    #     model = self.env.context.get('active_model')
    #     rec_model = self.env[model].browse(self.env.context.get('active_id'))
    #     partners = self.env['account.move.line'].search(
    #         [('move_id.user_id', '=', user.id), ('date', '>=', rec_model.start_date),
    #          ('date', '<=', rec_model.end_date),
    #          ('move_id.state', '=', 'posted'), ('account_id.account_type', '=', 'asset_receivable')], order="date asc").mapped('partner_id')
    #     account_obj = self.env['account.move.line']
    #     data_dict = []
    #     for partner in partners:
    #         debit = sum(account_obj.search(
    #             [('partner_id', '=', partner.id), ('date', '>=', rec_model.start_date),
    #              ('date', '<=', rec_model.end_date),
    #              ('move_id.state', '=', 'posted'), ('account_id.account_type', '=', 'asset_receivable')],
    #             order="date asc").mapped('debit'))
    #         data_dict.append({
    #             'partner': partner.name,
    #             'balance': debit,
    #         })
    #     return data_dict

    def get_print_date(self):
        now_utc_date = datetime.now()
        now_dubai = now_utc_date.astimezone(timezone('Asia/Karachi'))
        return now_dubai.strftime('%d/%m/%Y %H:%M:%S')

    def _get_report_values(self, docids, data=None):
        ledgers = self.get_partner_ledger()
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        return {
            'doc_ids': self.ids,
            'doc_model': 'ledger.report',
            'ledgers': ledgers,
            'print_date': self.get_print_date(),
            'login_user': self.env.user.name,

            'data': data,
            'partner': rec_model.partner_id.name,
            # 'get_partner_ledger': self.get_partner_ledger,
            # 'get_user_credit': self.get_user_credit,
            # 'get_users_customer': self.get_users_customer,
        }
