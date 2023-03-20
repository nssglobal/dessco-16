# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2022. All rights reserved.
{
    'name': 'Tally Trial Balance',
    'version': '16.0.0.1',
    'sequence': 1,
    'category': 'Accounting',
    'summary': 'Tally Type Trial Balance - Financial Report',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'description': """
    Tally Type Trial Balance
        """,
    'depends': ['accounting_pdf_reports','l10n_in'],
    'price': 35,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'data': [
        'security/ir.model.access.csv',
        'wizard/tally_trial_balance_wizard.xml',
        'report/tally_trial_balance_report.xml',
        'report/tally_trial_balance_report_template.xml',
        'views/dynamic_financial_report.xml',
        'report/trial_balance.xml',
    ],
    'assets': {
            'web.assets_backend': [
                    'tis_tally_trial_balance/static/src/js/trial_balance.js',
                    'tis_tally_trial_balance/static/src/xml/trial_balance.xml',
            ]
        },
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'live_test_url': 'https://www.youtube.com/watch?v=0OXaY-eqxq4'
}
