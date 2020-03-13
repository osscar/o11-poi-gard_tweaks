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
    'name': 'GARD Sale Price JS',
    'summary': 'Sale price rules and views',
    'descrption': """
Sale price rules and views
==========================
This module adds referential price rules (pricelist items)
for sale negotiation, type of sale, partner specific pricing, etc.

It also adds additional views and colors for enhanced management
and viewability, including:

* pricelist items on product form
* enhanced pricelist version form and tree views
* custom fields: sale price, unit price, pricelist version partner
* colored item lines for pricelists related to partners
* pricelists related to partner in partner form

- TO DO: security groups not set

""",
    'version': '11.01',
    'author': 'squid',
    'category': 'Sale Price',
    'license': 'AGPL-3',
    'complexity': 'easy',
    'images': [],
    'depends': [
        'base',
        'product',
        'sale',
    ],
    'demo': [],
    'data': [
        'data/gard_sale_price_data.xml',
        'views/gard_sale_price.xml',
        'views/gard_sale_price_templates.xml',
        'views/product_view.xml',
        'views/product_pricelist_view.xml',
        'views/res_partner.xml',
        'views/sale_view.xml',
    ],
    'qweb': [
        "static/src/xml/product_prices.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'test': [],
}
