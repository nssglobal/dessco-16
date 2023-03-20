# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2022. All rights reserved.

from odoo import fields, models
from datetime import datetime
from odoo.tools.misc import xlwt
import io
import base64
from xlwt import easyxf


class AccountingReport(models.TransientModel):
    _inherit = "accounting.report"

    report_type = fields.Selection([('normal', 'Normal'), ('tally', 'Tally')], string='Report Type', default='tally')
    bs_pl_summary_file = fields.Binary('Report')

    def print_tally_bs(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        return self.with_context(discard_logo_check=True)._print_bs_report(data)

    def _print_bs_report(self, data):
        data['form'].update(self.read(
            ['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp', 'account_report_id', 'enable_filter',
             'label_filter', 'target_move', 'report_type'])[0])
        return self.env.ref('tis_tally_bs_and_pl.action_report_tally_bs').report_action(self, data=data,
                                                                                           config=False)

    def export_tally_bs(self):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read()[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang') or 'en_US')
        account_lines = self.env['report.tis_tally_bs_and_pl.report_tally_bs'].get_account_lines(data['form'])
        start_date = ''
        end_date = ''
        if self.date_from:
            start_date = datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime(
                "%d-%m-%Y")
        if self.date_to:
            end_date = datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime(
                "%d-%m-%Y")
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Report', cell_overwrite_ok=True)
        format0 = easyxf('font:height 200;borders: left thin, right thin;')
        format_1 = easyxf('font:bold True;font:height 250; borders: right thin, bottom thin, top thin, left thin;')
        format_2 = easyxf('font:bold True;font:height 250; borders:  bottom thin, top thin;')
        format_3 = easyxf('font:bold True;font:height 250; borders: right thin, bottom thin, top thin;')
        format_4 = easyxf('font:bold True;font:height 250; borders: left thin, bottom thin, top thin;')
        format_5 = easyxf('font:bold True;font:height 250;')
        format_6 = easyxf('font:bold True;font:height 250;borders: right thin;')
        format_9 = easyxf('font:height 200; borders: left thin;')
        format_10 = easyxf('font:height 200;')
        format_11 = easyxf('font:height 200; borders: right thin;')
        format_13 = easyxf('borders: left thin;')
        worksheet.col(0).width = 8000
        worksheet.col(1).width = 4000
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 8000
        worksheet.col(4).width = 4000
        worksheet.col(5).width = 4000
        worksheet.col(16).width = 10000
        worksheet.col(17).width = 4000
        worksheet.col(18).width = 2000
        worksheet.col(19).width = 2000
        worksheet.col(20).width = 2000
        worksheet.col(21).width = 2000
        worksheet.row(5).height = 400
        worksheet.row(2).height = 400
        worksheet.row(4).height = 400
        worksheet.row(6).height = 400
        worksheet.row(7).height = 400
        worksheet.row(8).height = 400
        worksheet.row(9).height = 400
        worksheet.row(10).height = 400
        worksheet.row(11).height = 400
        worksheet.row(12).height = 400
        worksheet.write_merge(0, 1, 0, 2, data['form']['account_report_id'][1], format_1)
        if start_date and end_date:
            worksheet.write_merge(2, 2, 0, 2, start_date + ' ' + 'to' + ' ' + end_date,format0)
        elif start_date:
            worksheet.write_merge(2, 2, 0, 2, 'from' + ' ' + start_date, format0)
        elif end_date:
            worksheet.write_merge(2, 2, 0, 2, 'till' + ' ' + end_date, format0)
        else:
            worksheet.write_merge(2, 2, 0, 2, '', format0)
        worksheet.write(3, 3, '', format_10)
        worksheet.write(3, 4, '', format_10)
        worksheet.write(3, 5, '', format_10)
        worksheet.write(3, 2, '', format_11)
        worksheet.write(3, 0, '', format_13)
        worksheet.write(4, 1, '', format_2)
        worksheet.write(4, 2, '', format_3)
        worksheet.write(4, 4, '', format_2)
        worksheet.write(4, 5, '', format_3)
        row = 4
        col = 0
        row_n = 0
        for account in account_lines:
            worksheet.row(row).height = 400
            if account['account_type']=='account_type':
                flag = 0
                account_typ=account['name']
                worksheet.write(row, col, account_typ, format_2)
                for parent_type in account_lines:
                    if parent_type['parent_type']==account_typ:
                        if parent_type['name']==parent_type['parent_type']:
                            if flag==0:
                                row = row + 1
                                worksheet.write(row, col, parent_type['name'], format_5)
                                worksheet.write(row, col+2, parent_type['balance'], format_6)
                                total_balance=parent_type['balance']
                                flag=1
                            else:
                                row = row + 1
                                worksheet.write(row, col, parent_type['name'], format_9)
                                worksheet.write(row, col + 1, parent_type['balance'])
                        else:
                            row = row + 1
                            worksheet.write(row, col, parent_type['name'], format_9)
                            worksheet.write(row, col+1, parent_type['balance'])
                if row_n < row:
                    row_n=row
                col = col + 3
                row = 4
                worksheet.write(row_n+1, col-3, "Total", format_4)
                worksheet.write(row_n+1, col-1, total_balance, format_3)
                worksheet.write(row_n+1, col-2, '', format_2)
                for x in range(6, row_n+1):
                    worksheet.write(x, col-1, '', format_6)
        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.bs_pl_summary_file = excel_file
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=accounting.report&'
                   'field=bs_pl_summary_file&download=true&id=%s&filename=bs_pl_tally.xls' % self.id,
            'target': 'new',
        }

    def account_name(self, name):
        return ''.join([i for i in name if not i.isdigit()])

    def date_format(self, date):
        return datetime.strptime(date, '%Y-%m-%d').strftime(
            "%d-%m-%Y")


