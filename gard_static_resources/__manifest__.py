# -*- coding: utf-8 -*-
#    Author: squid
#    >>> Copyleft and swindle theft <<<
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
{
    'name': 'GARD Static Resources',
    'summary': 'GARD static resources',
    'descrption': """
GARD styles for views
==========================
This module adds referential price rules (pricelist items)
for price negotiation, sale type, partner specific pricing, etc.

It also adds additional views and colors for enhanced management
and viewability, including:

* pricelist items on product form
* enhanced form and tree views
* custom fields: sale price, unit price, pricelist partner
* colored item lines for pricelists related to partners
* pricelists related to partner in partner form

- TO DO: security groups not set

""",
    'version': '11.0.1.1.0',
    'author': 'squid',
    'category': 'Styles',
    'license': 'AGPL-3',
    'complexity': 'easy',
    'images': [],
    'depends': [
        'web',
    ],
    'demo': [],
    'data': [
        'views/report_templates.xml',
        'views/webclient_templates.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'test': [],
}
