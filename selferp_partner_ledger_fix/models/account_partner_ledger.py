import json

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.account_reports.models.account_partner_ledger import PartnerLedgerCustomHandler

from ..monkey_patch import monkey_patch


#
# Type: patch for BUG fixing
# Source Category: Enterprise
# Location: account_reports/models/account_partner_ledger.py
# Odoo version: 16
# Odoo version (at odoo.sh): 16.0.20230109
# Odoo sources revision: c5be51a5f02471e745543b3acea4f39664f8a820
# Enterprise sources revision: d3a8f601a98b3e997047a5c641fb3c4cf81b2732
#
# Description: Partner Ledger report never returns account move lines count
#              more than "Load More Limit" report settings even its PDF or
#              XLS downloading (in this case all lines expected, without
#              "Load more..." link).
#
@monkey_patch(PartnerLedgerCustomHandler)
def _report_expand_unfoldable_line_partner_ledger(self, line_dict_id, groupby, options, progress, offset, unfold_all_batch_data=None):
    def init_load_more_progress(line_dict):
        return {
            column['column_group_key']: line_col.get('no_format', 0)
            for column, line_col in  zip(options['columns'], line_dict['columns'])
            if column['expression_label'] == 'balance'
        }

    report = self.env.ref('account_reports.partner_ledger_report')
    markup, model, record_id = report._parse_line_id(line_dict_id)[-1]

    if markup != 'no_partner' and model != 'res.partner':
        raise UserError(_("Wrong ID for partner ledger line to expand: %s", line_dict_id))

    lines = []

    # Get initial balance
    if offset == 0:
        if unfold_all_batch_data:
            init_balance_by_col_group = unfold_all_batch_data['initial_balances'][record_id]
        else:
            init_balance_by_col_group = self._get_initial_balance_values([record_id], options)[record_id]
        initial_balance_line = report._get_partner_and_general_ledger_initial_balance_line(options, line_dict_id, init_balance_by_col_group)
        if initial_balance_line:
            lines.append(initial_balance_line)

            # For the first expansion of the line, the initial balance line gives the progress
            progress = init_load_more_progress(initial_balance_line)

    limit_to_load = report.load_more_limit + 1 if report.load_more_limit and not self._context.get('print_mode') else None

    if unfold_all_batch_data:
        aml_results = unfold_all_batch_data['aml_values'][record_id]
    else:
        aml_results = self._get_aml_values(options, [record_id], offset=offset, limit=limit_to_load)[record_id]

    has_more = False
    treated_results_count = 0
    next_progress = progress
    for result in aml_results:
        # =======> ORIGINAL
        # if report.load_more_limit and treated_results_count == report.load_more_limit:
        # <======= ORIGINAL
        # =======> FIXED
        if limit_to_load and treated_results_count == limit_to_load - 1:
        # <======= FIXED
            # We loaded one more than the limit on purpose: this way we know we need a "load more" line
            has_more = True
            break

        new_line = self._get_report_line_move_line(options, result, line_dict_id, next_progress)
        lines.append(new_line)
        next_progress = init_load_more_progress(new_line)
        treated_results_count += 1

    return {
        'lines': lines,
        'offset_increment': treated_results_count,
        'has_more': has_more,
        'progress': json.dumps(next_progress)
    }

