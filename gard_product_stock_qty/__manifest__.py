# -*- coding: utf-8 -*-
##############################################################################
#
#    Bli Bli, Ltd.
#    Copyleft and swindle theft.
#    Author: squid
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'GARD Product Stock Quantity',
    'version': '11.0.3.3.0',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Poduct stock availablity.',
    'descrption': """
Product stock availability
==========================
This module adds buttons and views to enhance product's
available stock visualization.

* stock quantity button in: product variants tree view, sale order line
* stock quantity menu in: sales menu, inventory menu
* kanban views include stock quantity button

- TO DO: security groups have not been specified
- TO DO: add stock quantity button to product template tree view

""",
    'images': [],
    'depends': [
        # 'product',
        # 'sale_stock',
        'stock_available',
        'gard_x_gard',
    ],
    'category': 'Stock',
    'data': [
        'views/gard_product_stock_qty_templates.xml',
        'views/product_view.xml',
        'views/stock_view.xml',
        'views/sale_view.xml',
        # 'security/ir.model.access.csv',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
