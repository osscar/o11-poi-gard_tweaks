# -*- coding: utf-8 -*-
# Copyright 2015-2016 Akretion - Alexis de Lattre
# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'GARD Stock Batch Picking',
    'version': '11.0.1.0.0',
    'category': 'Warehouse',
    'license': 'AGPL-3',
    'summary': 'GARD Stock Batch Picking customizations',
    'author': 'squid',
    'depends': [
        'fleet',
        'stock_batch_picking',
    ],
    'data': [
        'views/stock_batch_picking_view.xml',
        'views/stock_picking_view.xml',
    ],
    'installable': True,
}
