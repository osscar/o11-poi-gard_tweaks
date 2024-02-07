# -*- coding: utf-8 -*-
#    Author: squid
#    Copyleft and swindle theft
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

{
    'name': "GARD Order History",
    'summary': "Order picking and invoice history.",
    'version': '11.0.1.0.2',
    'author': 'squid',
    'category': 'Purchase, Sale',
    'description': """
GARD order history
==============================

Adds features to enhance view of the status of stock pickings
and invoices related to purchase and sales orders, as well as on related
tree views.

* adds a tab in order view
* customized tree view colors for enhanced visibility

- TO DO: add fields to supplier invoice view to customize colors
- TO DO: customize kanban views

    """,
    'license': 'AGPL-3',
    'complexity': 'easy',
    'images': [],
    'depends': [
        # 'account',
        # 'purchase',
        # 'sale',
        # 'stock',
        'web_tree_dynamic_colored_field',
        'gard_product_uom_pack',
        # 'gard_x_gard',
    ],
    # 'post_init_hook': 'post_init_hook',
    'demo': [],
    'data': [
        'data/account_data.xml',
        # 'data/config_data.xml',

        'views/account_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
    'application': False,
    'auto_install': False,
    'test': [],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
