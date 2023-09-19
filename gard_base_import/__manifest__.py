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
    "name": "GARD Import Model Data Wizard",
    "summary": "Create model records from model export lists.",
    "description": """
Wizard to create records from import file data based on model export lists. 
Export an export list data import template file. Security access groups for
export lists. Users/groups have access to allowed export lists.
""",
    "version": "11.0.0.0.1",
    "author": "squid",
    "category": "Extra Tools",
    "license": "AGPL-3",
    "depends": [
        "base_import",
    ],
    # 'demo': [],
    "data": [
        'wizard/import_model_data_view.xml',
        
        "security/gard_base_import_security.xml",
        "security/ir.model.access.csv",
        
        'views/ir_exports.xml',
    ],
    "qweb": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    # 'test': [],
}
