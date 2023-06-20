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
    'name': 'GARD x_Tweaks - Propagate',
    'version': '11.01',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Propagating wizards for POIESIS ODOO 11.0.',
    'descrption': """
GARD x_Tweaks - Propagate Wizard
==========================
This module tweaks the following:

* adds propagation wizard to add products to new order lines 
    * adds button to open product propagation wizard in:
        - purchase order
        - sale order
* adds propagation button to change routes on order lines:
    - sale order
* adds propagation button to change pricelist on order lines:
    - sale order
* adds propagation button to change pricelist on landed cost lines:
    - landed cost form

""",
    'images': [],
    'depends': [
        'account',
        'analytic',
        'gard_product_price',
        'gard_x_analytic',
        'gard_x_gard',
        'poi_x_gard',
        'purchase',
        # 'purchase_stock_analytic',
        'sale',
        # 'stock'
    ],
    'category': 'Other',
    'data': [
        'data/product_data.xml',
        'data/propagate_group_data.xml',

        'security/ir.model.access.csv',

        'views/propagate_group_view.xml',
        'views/purchase_view.xml',
        'views/sale_view.xml',
        'views/stock_landed_cost_view.xml',

        'wizard/propagate_account_analytic_view.xml',
        'wizard/propagate_product_view.xml',

    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
