{
    "name": "Stock Extension",
    "version": "16.0",
    "category": "Inventory",
    "summary": "Stock Extension",
    "author": "HAK Technologies",
    'license': 'LGPL-3',
    "depends": ["base","stock","sale_extension","basic_extension"],
    "data": [
            "views/stock.xml", 
            'report/delivery_slip.xml',
            'report/report_delivery_order.xml',
    ],
    "installable": True,
}
