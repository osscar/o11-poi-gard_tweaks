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
    'name': 'GARD x_Tweaks - Analytic Accounting',
    'version': '11.0.1.1.0',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Analytic Accounting Tweaks for poi_Odoov11.',
    'descrption': """
GARD x_Tweaks - Analytic Accounting
==========================
This module tweaks the following:

* adds a wizard to call account_move_analytic_recreate write enhancement to recreate analytic lines
* adds filters using account_analytic_parent / analytic_base_department fields
*


""",
    'images': [],
    'depends': [
        'account_analytic_parent',
        'account_move_analytic_recreate',
        'analytic_base_department',
        'gard_x_gard',
        'stock_landed_costs_analytic',
    ],
    'category': 'Other',
    'data': [
        'views/account_view.xml',
        'views/account_analytic_view.xml',
        'views/account_invoice_view.xml',
        'views/stock_landed_cost_view.xml',

        'wizard/account_move_analytic_recreate_view.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
