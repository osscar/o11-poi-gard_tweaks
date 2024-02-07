# -*- coding: utf-8 -*-
##############################################################################
#
#    bliblibli Corp. Unltd.
#    Copyleft and swindle theft
#    Author: squid
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
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
    'name': 'GARD Stock Force Date',
    'version': '11.01',
    'summary': 'Force Date in Stock Picking',
    'description': """
    This module will give you a way to record stock picking to a specific date,
    which will effect on related moves and stock journal entries.
    """,
    'author': 'squid',
    'company': 'GARD',
    'website': "https://www.gardsrl.com/",
    'category': 'Warehouse',
    'depends': [
        # 'stock', 
        'stock_account', 
        'poi_stock_account_consolidate'
    ],
    'data': [
        'security/gard_stock_force_date_security.xml',

        'views/stock_view.xml',
    ],
    'demo': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': False
}
