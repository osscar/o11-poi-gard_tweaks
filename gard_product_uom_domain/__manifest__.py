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
    'name': 'GARD Product UoM Domain',
    'summary': 'Restrict product UoM in views',
    'descrption': """
Product UoM domains in views
==========================
Adds product UoM domains in view fields to restrict the selectable UoMs to product template uom parameters.
""",
    'version': '11.0.0.1.0',
    'author': 'squid',
    'category': 'Product',
    'license': 'AGPL-3',
    'complexity': 'easy',
    'images': [],
    'depends': [
        'product',
        'purchase',
        'sale',
        'gard_x_gard',
    ],
    'demo': [],
    'data': [
        'views/product_template_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'test': [],
}
