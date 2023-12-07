# -*- coding: utf-8 -*-
# Copyright 2015-2016 Akretion - Alexis de Lattre
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'GARD Partner External Maps',
    'version': '11.0.1.0.0',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'summary': 'Add Multi Record Map and Map Routing ',
    'author': 'squid',
    'depends': [
        'partner_external_map',
        'stock',
        # 'stock_batch_picking',
    ],
    'data': [
        'views/res_partner_view.xml',
        'views/stock_view.xml',
        # 'views/stock_batch_picking_view.xml',
        'data/map_website_data.xml',
    ],
    'installable': True,
}
