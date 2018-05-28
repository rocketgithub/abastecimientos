# -*- coding: utf-8 -*-
{
    'name': "Abastecimientos",

    'summary': """Abastecimientos""",

    'description': """
        Abastecimientos
    """,

    'author': "aquíH",
    'website': "http://www.aquih.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['stock'],

    'data': [
        'wizard/crear_abastecimiento.xml',
        'views/abastecimientos_views.xml',
        'views/stock_picking_views.xml',
    ],
}
