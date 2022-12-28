# -*- coding: utf-8 -*-
{
    'name': "Order line quantity",

    'summary': """
       Dessco order line quantity""",

    'description': """
         Dessco order line quantity
    """,

    'author': "Infotech",
    'website': "https://www.infotech.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    "license": "AGPL-3",

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
