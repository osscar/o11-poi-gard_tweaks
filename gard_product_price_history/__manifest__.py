# -*- coding: utf-8 -*-
#    Author: squid
#    >>> Copyleft and swindle theft <<<
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
    'name': 'GARD Product Price History',
    'summary': 'Product price history',
    'descrption': """
Product price history
==========================
This module records historical referential product prices 
from pricelist items, which helps keep track of price trends
and modifications.

""",
    'version': '11.0.0.0.1',
    'author': 'squid',
    'category': 'Product Price',
    'license': 'AGPL-3',
    'complexity': 'easy',
    'images': [],
    'depends': [
        'product',
    ],
    'demo': [],
    'data': [
        # 'security/gard_product_price_history_security.xml',
        # 'security/ir.model.access.csv',

        'views/product_template_view.xml',
        'views/product_view.xml',
        'views/product_pricelist_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'test': [],
}
