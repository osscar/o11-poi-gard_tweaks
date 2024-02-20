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
    'name': 'Bolivia Accounting - Invoice Reference Checks',
    'version': '11.0.1.0.1',
    'author': 'squid',
    'company': '',
    'website': 'http://wwf.comcom.com',
    'summary': 'Invoice reference checks for Bolivia accounting.',
    'descrption': """
Account Invoice Reference Checks
==========================
Extended invoice reference checks for Bolivian accounting.

eg. localized duplicate supplier references.
""",
    'images': [],
    'depends': [
        "account",
        'gard_l10n_bo',
    ],
    'category': 'Account',
    'data': [
        # 'views/sale_view.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
