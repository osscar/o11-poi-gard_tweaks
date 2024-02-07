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
    "name": "GARD Invoice Refund Requests",
    "summary": "Invoice refund requests",
    "description": """
Adds refund request vouchers to aid delegation, supervision and traceability, 
from which the refund data is obtained to process the refund.
""",
    "version": "11.0.0.1.1",
    "author": "squid",
    "category": "Localization",
    "license": "AGPL-3",
    "depends": [
        # "account",
        # "purchase",
        # "sale",
        # "sale_stock",
        # "poi_bol_base",
        # "poi_bol_siat",
        # "gard_x_gard",
        "gard_l10n_bo",
    ],
    # 'demo': [],
    "data": [
        'wizard/account_invoice_refund_view.xml',
        
        'data/ir_sequence_data.xml',
        
        "security/gard_account_invoice_refund_security.xml",
        "security/ir.model.access.csv",
        
        'views/account_invoice_view.xml',
        'views/account_invoice_refund_request_view.xml',
    ],
    "qweb": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    # 'test': [],
}
