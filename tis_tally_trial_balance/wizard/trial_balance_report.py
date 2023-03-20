# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2021. All rights reserved.

import time
from odoo import fields, models, api, _

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import io
import json
from odoo.http import request
from odoo.exceptions import UserError


class AccountTrialBalance(models.TransientModel):
    _inherit = "account.common.report"
    _name = 'account.report_trialbalance'

    journal_ids = fields.Many2many('account.journal',

                                   string='Journals', required=True,
                                   default=[])
    display_account = fields.Selection(
        [('all', 'All'), ('movement', 'With movements'),
         ('not_zero', 'With balance is not equal to 0')],
        string='Display Accounts', required=True, default='movement')

    @api.model
    def action_view_report(self, data):
        rec = self.env['account.report_trialbalance'].search([('id', '=', data[0])])
        values = {
            'display_account': rec.display_account,
            'model': self,
            'journals': rec.journal_ids,
            'target_move': rec.target_move,

        }
        # data=rec.read()
        if rec.date_from:
            values.update({
                'date_from': rec.date_from,
            })
        if rec.date_to:
            values.update({
                'date_to': rec.date_to,
            })

        filters = self.get_filter(data)
        print("filters", filters)
        records = self._get_report_values(values)
        print("records", records)
        currency = self._get_currency()

        return {
            'name': "Trial Balance",
            'type': 'ir.actions.client',
            'tag': 'trial_balance_report',
            'filters': filters,
            'report_lines': records['Accounts'],
            'debit_total': records['debit_total'],
            'credit_total': records['credit_total'],
            'currency': currency,
        }

    def get_filter(self, option):
        data = self.get_filter_data(option)
        filters = {}
        if data.get('journal_ids'):
            filters['journals'] = self.env['account.journal'].browse(data.get('journal_ids')).mapped('code')
        else:
            filters['journals'] = ['All']
        if data.get('target_move'):
            filters['target_move'] = data.get('target_move')
        if data.get('date_from'):
            filters['date_from'] = data.get('date_from')
        if data.get('date_to'):
            filters['date_to'] = data.get('date_to')

        filters['company_id'] = ''
        filters['journals_list'] = data.get('journals_list')
        filters['company_name'] = data.get('company_name')
        filters['target_move'] = data.get('target_move').capitalize()

        return filters

    def get_filter_data(self, option):
        r = self.env['account.report_trialbalance'].search([('id', '=', option[0])])
        default_filters = {}
        company_id = self.env.companies.ids
        company_domain = [('company_id', 'in', company_id)]
        journal_ids = r.journal_ids if r.journal_ids else self.env['account.journal'].search(company_domain,
                                                                                             order="company_id, name")

        journals = []
        o_company = False
        for j in journal_ids:
            if j.company_id != o_company:
                journals.append(('divider', j.company_id.name))
                o_company = j.company_id
            journals.append((j.id, j.name, j.code))

        filter_dict = {
            'journal_ids': r.journal_ids.ids,
            'company_id': company_id,
            'date_from': r.date_from,
            'date_to': r.date_to,
            'target_move': r.target_move,
            'journals_list': journals,
            # 'journals_list': [(j.id, j.name, j.code) for j in journals],

            'company_name': ', '.join(self.env.companies.mapped('name')),
        }
        filter_dict.update(default_filters)
        return filter_dict

    @api.model
    def _get_currency(self):
        journal = self.env['account.journal'].browse(
            self.env.context.get('default_journal_id', False))
        if journal.currency_id:
            return journal.currency_id.id
        lang = self.env.user.lang
        if not lang:
            lang = 'en_US'
        lang = lang.replace("_", '-')
        currency_array = [self.env.company.currency_id.symbol,
                          self.env.company.currency_id.position, lang]
        return currency_array

    def _get_report_values(self, data=None):
        docs = data['model']
        display_account = data['display_account']
        accounts = self.env['account.account'].search([])
        if not accounts:
            raise UserError(_("No Accounts Found! Please Add One"))
        filter_accounts = self._get_filter_accounts(accounts, display_account, data)
        total_debit = sum(x['debit'] for x in filter_accounts)
        total_credit = sum(x['credit'] for x in filter_accounts)
        return {
            'doc_ids': self.ids,
            'debit_total': total_debit,
            'credit_total': total_credit,
            'docs': docs,
            'time': time,
            'Accounts': filter_accounts,
        }

    def _get_filter_accounts(self, accounts, display_account, data):

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        if data['target_move'] == 'posted':
            filters += " AND account_move_line.parent_state = 'posted'"
        else:
            filters += " AND account_move_line.parent_state in ('draft','posted')"
        if data.get('date_from'):
            filters += " AND account_move_line.date >= '%s'" % data.get('date_from')
        if data.get('date_to'):
            filters += " AND account_move_line.date <= '%s'" % data.get('date_to')

        if data['journals']:
            filters += ' AND jrnl.id IN %s' % str(tuple(data['journals'].ids) + tuple([0]))
        tables += ' JOIN account_journal jrnl ON (account_move_line.journal_id=jrnl.id)'
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_filtered = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            res['code'] = account.code
            res['name'] = account.name
            res['id'] = account.id
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            if data.get('date_from'):
                res['Init_balance'] = self.get_balance(account, display_account, data)
            if display_account == 'all':
                account_filtered.append(res)

            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'not_zero' and not currency.is_zero(
                    res['balance']):
                account_filtered.append(res)
            if display_account == 'movement' and (
                    not currency.is_zero(res['debit']) or not currency.is_zero(
                res['credit'])):
                account_filtered.append(res)
        return account_filtered

    def get_balance(self, account, display_account, data):
        if data.get('date_from'):

            tables, where_clause, where_params = self.env[
                'account.move.line']._query_get()
            tables = tables.replace('"', '')
            if not tables:
                tables = 'account_move_line'
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            if data['target_move'] == 'posted':
                filters += " AND account_move_line.parent_state = 'posted'"
            else:
                filters += " AND account_move_line.parent_state in ('draft','posted')"
            if data.get('date_from'):
                filters += " AND account_move_line.date < '%s'" % data.get('date_from')

            if data['journals']:
                filters += ' AND jrnl.id IN %s' % str(tuple(data['journals'].ids) + tuple([0]))
            tables += ' JOIN account_journal jrnl ON (account_move_line.journal_id=jrnl.id)'

            # compute the balance, debit and credit for the provided accounts
            request = (
                    "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                    " FROM " + tables + " WHERE account_id = %s" % account.id + filters + " GROUP BY account_id")
            params = tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                return row

    def get_xlsx_Trial_balance_report(self, data, response, report_data, dfr_data):
        report_data_main = json.loads(report_data)
        output = io.BytesIO()
        filters = json.loads(data)
        total = json.loads(dfr_data)
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        head = workbook.add_format({'align': 'center', 'bold': True,
                                    'font_size': '20px'})
        heading_style_2 = workbook.add_format(
            {'bold': True,
             'align': 'center',
             'font_size': '10px',
             'border': 1,
             'border_color': 'black'})
        text = workbook.add_format({'border': 1, 'font_size': '10px'})
        normal_txt = workbook.add_format({'bold': True, 'font_size': '10px', 'border': 1})
        sheet.merge_range('A2:D3', filters.get('company_name') + ':' + ' Trial Balance', head)
        date = workbook.add_format({'align': 'center', 'bold': True,
                                         'font_size': '10px'})
        if filters.get('date_from'):
            sheet.merge_range('A5:B5', 'From: ' + filters.get('date_from'), date)
        if filters.get('date_to'):
            sheet.merge_range('C5:D5', 'To: ' + filters.get('date_to'), date)
        sheet.merge_range('A6:D6', 'Journals: ' + ', '.join(
            [lt or '' for lt in filters['journals']]) + '  Target Moves: ' + filters.get('target_move'), date)
        sheet.write('A8', 'Code', heading_style_2)
        sheet.write('B8', 'Account', heading_style_2)
        if filters.get('date_from'):
            sheet.write('C8', 'Initial Debit', heading_style_2)
            sheet.write('D8', 'Initial Credit', heading_style_2)
            sheet.write('E8', 'Debit', heading_style_2)
            sheet.write('F8', 'Credit', heading_style_2)
        else:
            sheet.write('C8', 'Debit', heading_style_2)
            sheet.write('D8', 'Credit', heading_style_2)

        row = 7
        col = 0
        sheet.set_column(5, 0, 15)
        sheet.set_column(6, 1, 15)
        sheet.set_column(7, 2, 26)
        if filters.get('date_from'):
            sheet.set_column(8, 3, 15)
            sheet.set_column(9, 4, 15)
            sheet.set_column(10, 5, 15)
            sheet.set_column(11, 6, 15)
        else:

            sheet.set_column(8, 3, 15)
            sheet.set_column(9, 4, 15)
        for rec_data in report_data_main:

            row += 1
            sheet.write(row, col, rec_data['code'], text)
            sheet.write(row, col + 1, rec_data['name'], text)
            if filters.get('date_from'):
                if rec_data.get('Init_balance'):
                    sheet.write(row, col + 2, rec_data['Init_balance']['debit'], text)
                    sheet.write(row, col + 3, rec_data['Init_balance']['credit'], text)
                else:
                    sheet.write(row, col + 2, 0, text)
                    sheet.write(row, col + 3, 0, text)

                sheet.write(row, col + 4, rec_data['debit'], text)
                sheet.write(row, col + 5, rec_data['credit'], text)

            else:
                sheet.write(row, col + 2, rec_data['debit'], text)
                sheet.write(row, col + 3, rec_data['credit'], text)
        sheet.write(row + 1, col, 'Total', heading_style_2)
        sheet.write(row + 1, col+1, '', heading_style_2)
        if filters.get('date_from'):
            sheet.write(row + 1, col + 4, total.get('debit_total'), normal_txt)
            sheet.write(row + 1, col + 5, total.get('credit_total'), normal_txt)
            sheet.write(row + 1, col + 2, '', normal_txt)
            sheet.write(row + 1, col + 3, '', normal_txt)
        else:
            sheet.write(row + 1, col + 2, total.get('debit_total'), normal_txt)
            sheet.write(row + 1, col + 3, total.get('credit_total'), normal_txt)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
