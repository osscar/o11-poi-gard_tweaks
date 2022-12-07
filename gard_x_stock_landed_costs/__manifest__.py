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
    'name': 'GARD x_Tweaks - Stock Landed Costs',
    'version': '11.01',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Stock Landed Cost Tweaks for poi_Odoov11.',
    'descrption': """
GARD x_Tweaks - Stock Landed Costs
==========================
This module tweaks the following:

* adds cost line field value update onchange cost line
analytic account.
* adds propagation of landed cost form cost lines 
based on analytic account lines
*


""",
    'images': [],
    'depends': [
        'account',
        'analytic',
        'gard_x_gard',
        # 'poi_x_gard',
        # 'poi_bol_base',
        # 'poi_kardex_valorado',
        # 'poi_stock_account_consolidate',
        # 'sale',
        # 'stock',
        # 'stock_account',
        'stock_landed_costs',
        'stock_landed_costs_analytic',
    ],
    'category': 'Other',
    'data': [

        'views/stock_landed_cost_view.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
