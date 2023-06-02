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
        'analytic',
        #'crm',
        #'crm_livechat',
        'poi_x_gard',
        'poi_bol_base',
        'poi_bol_siat',
        'poi_kardex_valorado',
        'poi_payment_request',
        'poi_stock_account_consolidate',
        'sale',
        #'sale_crm',
        'sale_stock',
        'stock',
        'stock_account',
        'stock_landed_costs',
        'stock_landed_costs_analytic',
        'web',
        #'website',
        #'website_crm',
        #'website_sale',
        #'website_theme_flexible',
    ],
    'category': 'Other',
    'data': [
        # 'data/fetchmail.server.csv',
        #'data/res_config_data.xml',
        'data/gard_x_gard_data.xml',

        'report/account_report_views.xml',
        'report/account_report_templates.xml',

        #'res/res.lang.csv',

        'security/gard_x_gard_security.xml',
        'security/ir.model.access.csv',

        'views/account_view.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        'views/product_views.xml',
        #'views/res_company_view.xml',
        'views/sale_view.xml',
        'views/stock_view.xml',
        'views/stock_landed_cost_view.xml',
        #'views/website_templates.xml',
    ],
    'demo': [],
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'auto_install': False,
}
