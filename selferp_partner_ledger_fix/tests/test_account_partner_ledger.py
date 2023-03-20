from odoo import fields
from odoo.fields import Command
from odoo.tests import tagged

from odoo.addons.account_reports.models.account_partner_ledger import PartnerLedgerCustomHandler
from odoo.addons.account_reports.tests.common import TestAccountReportsCommon


@tagged('post_install', '-at_install')
class TestPartnerLedgerCustomHandler(TestAccountReportsCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.report = cls.env.ref('account_reports.partner_ledger_report')

        #
        # fill test data
        #
        partner = cls.partner_a
        account_payable = cls.company_data['default_account_payable']
        account_receivable = cls.company_data['default_account_receivable']

        lines = []
        for i in range(100):
            values = {
                'name': f'Test line #{i}',
                'partner_id': partner.id,
            }

            if i % 3:
                values.update({
                    'debit': 0.0,
                    'credit': 100 + i,
                    'account_id': account_receivable.id,
                })
            else:
                values.update({
                    'debit': 100 + i,
                    'credit': 0.0,
                    'account_id': account_payable.id,
                })

            lines.append(Command.create(values))

        cls.test_move = cls.env['account.move'].create({
            'move_type': 'entry',
            'date': fields.Date.from_string('2023-01-15'),
            'journal_id': cls.company_data['default_journal_misc'].id,
            'line_ids': lines,
        })
        cls.test_move.action_post()

    def test__report_expand_unfoldable_line_partner_ledger(self):
        # switch on print mode
        report = self.report.with_context(print_mode=True)
        report_handler = report.env['account.partner.ledger.report.handler']

        partner = self.partner_a
        line_dict_id = self.report._get_generic_line_id(partner._name, partner.id)
        options = self._generate_options(
            report,
            fields.Date.from_string('2023-01-01'),
            fields.Date.from_string('2023-12-31'),
        )
        progress = {
            column['column_group_key']: 0.0 for column in options['columns']
        }

        #
        # check bug existing
        #
        report.load_more_limit = 3

        # get original (not patched) method (with bug)
        original_method = getattr(PartnerLedgerCustomHandler, '_report_expand_unfoldable_line_partner_ledger').super

        result = original_method(
            report_handler,
            line_dict_id,
            None,
            options,
            progress,
            0,
            unfold_all_batch_data=None,
        )

        self.assertTrue(result.get('has_more'))
        self.assertEqual(len(result.get('lines')), 3)

        #
        # check patched (fixed) method
        #
        report.load_more_limit = 80

        result = report_handler._report_expand_unfoldable_line_partner_ledger(
            line_dict_id,
            None,
            options,
            progress,
            0,
            unfold_all_batch_data=None,
        )

        self.assertFalse(result.get('has_more'))
        self.assertEqual(len(result.get('lines')), 100)

        #
        # check patched (fixed) method: non-print mode
        #
        report.load_more_limit = 80

        result = report_handler.with_context(print_mode=False)._report_expand_unfoldable_line_partner_ledger(
            line_dict_id,
            None,
            options,
            progress,
            0,
            unfold_all_batch_data=None,
        )

        self.assertTrue(result.get('has_more'))
        self.assertEqual(len(result.get('lines')), 80)

