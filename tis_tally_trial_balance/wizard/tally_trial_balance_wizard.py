# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2022. All rights reserved.

from odoo import fields, models, _
from datetime import datetime
from odoo.tools.misc import xlwt
import io
import base64
from xlwt import easyxf


class AccountBalanceReport(models.TransientModel):
    _inherit = "account.balance.report"

    report_type = fields.Selection([('normal', 'Normal'), ('tally', 'Tally')], string="Report Type",
                                   default='tally')
    trial_balance_file = fields.Binary('Report')

    def check_report_tally_trial_balance(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self.with_context(discard_logo_check=True)._print_report_tally_trial_balance(data)

    def _print_report_tally_trial_balance(self, data):
        data = self.pre_print_report(data)
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('tis_tally_trial_balance.action_tally_trial_balance').report_action(records, data=data)

    def print_tally_trial_balance_xls_report(self):
        datas = {}
        datas['model'] = 'account.balance.report'
        datas['form'] = self.read()[0]
        print_time = datetime.strptime(str(datetime.now().replace(microsecond=0)), '%Y-%m-%d %H:%M:%S').strftime(
            '%d-%m-%Y %H:%M:%S')
        display_account = datas['form'].get('display_account')
        accounts = self.env['account.account'].search([])
        account_res = self.env['report.accounting_pdf_reports.report_trialbalance']._get_accounts(accounts,
                                                                                                  display_account)
        company_id = self.env.user.company_id.name
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('trial_balance', cell_overwrite_ok=True)
        bold = easyxf('font:bold True;font:height 280; align: horiz center;')
        bold_left = easyxf('font:bold True;font:height 250;')
        bold_right = easyxf('font:bold True; align: horiz right;font:height 250;')
        text_left = easyxf('font:height 250;')
        text_right = easyxf('font:height 250; align: horiz right;')
        time = easyxf('font:height 250; align: horiz right;')
        bg_color = easyxf('font:bold True; align: horiz center; pattern: pattern solid,'
                          ' fore_colour gray25;font:height 250;')
        worksheet.col(0).width = 7000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 7000
        worksheet.col(4).width = 7000
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 5000
        worksheet.col(7).width = 5000
        worksheet.row(2).height = 400
        worksheet.row(3).height = 400
        worksheet.row(4).height = 400
        worksheet.row(5).height = 400
        worksheet.row(6).height = 400
        worksheet.row(7).height = 400
        worksheet.write(2, 3, 'Printed At :', time)
        worksheet.write(2, 4, print_time, time)
        worksheet.write_merge(3, 3, 4, 4, '')
        worksheet.write_merge(3, 5, 0, 2, 'Particulars', bold)
        worksheet.write_merge(3, 3, 3, 4, company_id, bold)
        if self.date_from and self.date_to:
            date = datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime(
                '%d-%m-%Y') + ' to ' + datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime(
                '%d-%m-%Y')
            worksheet.write_merge(4, 4, 3, 4, date, bold)
        worksheet.write_merge(5, 5, 3, 4, 'Trial Balance', bold)
        worksheet.write_merge(6, 6, 0, 4, '', bg_color)
        worksheet.write_merge(7, 7, 0, 2, '', bg_color)
        worksheet.write(7, 3, 'Debit Balance', bg_color)
        worksheet.write(7, 4, 'Credit Balance', bg_color)
        row = 8
        col = 0
        for account in account_res:
            worksheet.row(row).height = 400
            if display_account == 'all':
                worksheet.write(row, col, account['name'], text_left)
            if account['balance'] == 0:
                worksheet.write(row, col + 3, account['balance'], text_right)
                worksheet.write(row, col + 4, abs(account['balance']), text_right)
            if account['balance'] > 0:
                worksheet.write(row, col + 3, account['balance'], text_right)
            if account['balance'] < 0:
                worksheet.write(row, col + 4, abs(account['balance']), text_right)
            row = row + 1
        worksheet.row(row).height = 400
        worksheet.write(row, col, 'Grand Total', bold_left)
        worksheet.write(row, col + 3, xlwt.Formula('SUM(D9:D%s)' % (str(row))), bold_right)
        worksheet.write(row, col + 4, xlwt.Formula('SUM(E9:E%s)' % (str(row))), bold_right)
        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.trial_balance_file = excel_file
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=account.balance.report&'
                   'field=trial_balance_file&download=true&id=%s&filename=bs_pl_tally.xls' % self.id,
            'target': 'new',
        }
