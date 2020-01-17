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
    'version': '11.02',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Poduct stock availablity.',
    'descrption': """
Product stock availability
==========================
This module adds buttons and views to enhance useability for the
visualization of a product's available stock.

* button in product variants tree view
* button in sale order line
* product stock quantity menu in sales menu
* product stock quantity menu in inventory menu
* kanban views include button

- security groups have not been specified yet

""",
    'images': [],
    'depends': [
        'product',
        'sale',
        'stock',
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
    'application': True,
    'installable': True,
    'auto_install': False,
}
