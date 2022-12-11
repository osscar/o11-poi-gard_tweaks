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
    'name': 'GARD x_Tweaks - Purchase',
    'version': '11.01',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Stock Landed Cost Tweaks for poi_Odoov11.',
    'descrption': """
GARD x_Tweaks - Purchase
==========================
This module tweaks the following:

* adds propagation tool of analytic account to po lines 
* adds analytic account create wizard


""",
    'images': [],
    'depends': [
        'account',
        'analytic',
        'gard_x_analytic',
        'gard_x_gard',
        'purchase',
        'purchase_stock_analytic',
    ],
    'category': 'Other',
    'data': [
        'wizard/purchase_order_account_analytic_create_view.xml',
        'views/purchase_view.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
