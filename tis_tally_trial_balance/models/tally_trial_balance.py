# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2022. All rights reserved.

from odoo import api, models, _


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.tis_tally_trial_balance.report_tally_trial_balance'
    _inherit = 'report.accounting_pdf_reports.report_trialbalance'
