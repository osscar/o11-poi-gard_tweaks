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
    'name': 'MRP Product Stock Quantity',
    'version': '11.0.1.1.0',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Poduct stock availablity.',
    'descrption': """
MRP Product Stock Availability
==========================
Show potential product quantity for manufactured products.
""",
    'images': [],
    'depends': [
        # 'product',
        'stock_available_mrp',
        'gard_product_stock_qty',
    ],
    'category': 'Stock',
    'data': [
        # 'views/product_view.xml',
        # 'views/stock_view.xml',
        'views/sale_view.xml',
        # 'security/ir.model.access.csv',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
