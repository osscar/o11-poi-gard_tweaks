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
    'version': '3.01',
    'author': 'squid',
    'category': 'Purchase, Sale',
    'description': """
GARD order history
==============================

Adds feature to enhance view of the status stock pickings
and invoices related to purchase and sales orders.

* adds a tab in order view
* customized tree view colors for enhanced visibility

    """,
    'license': 'AGPL-3',
    'complexity': 'easy',
    'images': [],
    'depends': [
        'account',
        'bo_invoice',
        'purchase',
        'sale',
        'stock',
    ],
    'demo': [],
    'data': [
        'views/account_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
    'application': True,
    'auto_install': False,
    'test': [],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
