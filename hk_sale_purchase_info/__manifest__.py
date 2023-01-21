# -*- coding: utf-8 -*-
{
    'name': "Sale/Purchase Report",

    'summary': """
        Sale/Purchase  Report""",

    'description': """
        Sale/Purchase  Report
    """,

    'author': "HAK Tech",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/report_wizard.xml',
    ],

}
