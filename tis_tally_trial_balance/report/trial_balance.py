from odoo import api, models, _


class TrialBalance(models.AbstractModel):
    _name = 'report.tis_tally_trial_balance.trial_balance'

    @api.model
    def _get_report_values(self, docids, data=None):
        if self.env.context.get('trial_dynamic_pdf_report'):

            if data.get('report_data'):
                data.update({'account_data': data.get('report_data')['report_lines'],
                             'filters': data.get('report_data')['filters'],
                             'debit': data.get('report_data')['debit_total'],
                             'credit': data.get('report_data')['credit_total'],
                             'company': self.env.company,
                             })
        return data
