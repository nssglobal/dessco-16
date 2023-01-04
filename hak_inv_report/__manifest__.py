# -*- coding: utf-8 -*-
{
    'name': "TAX invoice Report",

    'summary': """
       TAX invoice Report""",

    'description': """
       TAX invoice Report
    """,

      "author": "HAK Technologies",
    'website': "https://www.haktechnologies.com",
    "images": ["static/description/icon.png"],
    "license": "AGPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '16.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'reports/report.xml',
        'reports/invoice_template.xml',
    ],

}
