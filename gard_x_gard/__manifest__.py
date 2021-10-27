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
    'name': 'GARD x_Tweaks',
    'version': '11.01',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Tweaks for poi_Odoov11.',
    'descrption': """
GARD x_Tweaks
==========================
This module tweaks the following:

*
*
*


""",
    'images': [],
    'depends': [
        'account',
        'poi_x_gard',
        'poi_bol_base',
        'sale',
        'web',
    ],
    'category': 'Other',
    'data': [
        'report/account_report_views.xml',
        'report/account_report_templates.xml',

        'security/gard_x_gard_security.xml',

        'views/account_view.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
