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
        'poi_x_gard',
        'poi_payment_request',
        'poi_bol_payment_request',
        'account',
        'web',
    ],
    'category': 'Other',
    'data': [
        'security/gard_x_gard_security.xml',
        'views/account_payment_view.xml',
        'views/account_expenses_rendition_view.xml',
        'views/account_deposit_view.xml',
        'report/account_deposit_report.xml',
        'report/account_deposit_report_templates.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
