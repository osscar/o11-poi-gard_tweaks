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
    'name': 'MRP Sale Product Margin',
    'version': '11.0.1.0.2',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Sales margins based on product BoMs.',
    'descrption': """
MRP Sales and Product Margins
==========================
This module extends the sale order line, computing margin for
products with BoMs.

*
*
*

""",
    'images': [],
    'depends': [
        # 'product',
        # 'mrp',
        'gard_sale_product_margin',
        # 'mrp_product_stock_qty',
        # 'product_margin',
        # 'sale_margin',
    ],
    'category': 'Sales',
    'data': [
        # 'security/gard_sale_product_margin_security.xml',
        # 'security/ir.model.access.csv',
        # 'views/sale_margin_view.xml',
        # 'views/product_product_views.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
