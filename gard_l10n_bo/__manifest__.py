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
    "name": "GARD Bolivia - Accounting",
    # 'summary': '',
    "description": """
Fiscal accounting localization for Bolivia customized
by GARD based on POIESIS\' customizations

- sales journal based on subsidiary (sucursal)

""",
    "version": "11.02",
    "author": "squid",
    "category": "Localization",
    "license": "AGPL-3",
    # 'complexity': 'easy',
    # 'images': [],
    "depends": [
        "poi_bol_base",
        "poi_bol_siat",
        "poi_warehouse",
        "poi_warehouse_invoice",
    ],
    # 'demo': [],
    "data": [
        'report/basic_invoice.xml',
        'report/invoice_base.xml',
        'report/siat_invoice.xml',

        'views/dosif_view.xml',
        'views/product_uom_view.xml',
        'views/stock_warehouse_view.xml',
    ],
    "qweb": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    # 'test': [],
}
