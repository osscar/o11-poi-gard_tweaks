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
    'name': 'GARD Product Price',
    'summary': 'Product price rules and views',
    'descrption': """
Product price rules and views
==========================
This module adds referential price rules (pricelist items)
for price negotiation, sale type, partner specific pricing, etc.

It also adds additional views and colors for enhanced management
and viewability, including:

* pricelist items on product form
* enhanced form and tree views
* custom fields: sale price, unit price, net sale margin, pricelist partner
* colored item lines for pricelists related to partners
* pricelists related to partner in partner form

- TO DO: customer savings field
- TO DO: decoration colors on views
- TO DO: display record when clicking many_2many_tags (extend
JS script on web/static/src/js in render_tag function.)

""",
    'version': '11.02',
    'author': 'squid',
    'category': 'Product Price',
    'license': 'AGPL-3',
    'complexity': 'easy',
    'images': [],
    'depends': [
        'base',
        'base_import',
        'product',
        'sale',
        'sale_stock',
        'gard_sale_product_margin',
        'gard_static_resources',
    ],
    'demo': [],
    'data': [
        'security/gard_product_price_security.xml',
        'security/ir.model.access.csv',

        'data/gard_product_price_data.xml',

        'report/product_reports.xml',
        'report/product_pricelist_templates.xml',

        'views/product_template_view.xml',
        'views/product_view.xml',
        'views/product_pricelist_view.xml',
        'views/res_partner.xml',
        'views/sale_view.xml',

        'wizard/product_price_list_views.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'test': [],
}
