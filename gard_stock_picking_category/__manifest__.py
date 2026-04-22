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
    "name": "GARD Stock Picking Category",
    "version": "11.0.1.0.0",
    "author": "squid",
    "company": "",
    "website": "http://wwf.comcom.com",
    "summary": "Tweaks for poi_Odoov11.",
    "descrption": """
GARD Stock Picking Category
==========================
This module tweaks the following:

* Stock picking categories are now set on the picking form. This allows for better reporting and categorization of pickings.
*
*


""",
    "images": [],
    "depends": [
        "stock",
        "gard_order_history",
        "gard_x_gard",
    ],
    "category": "Other",
    "data": [
        "views/stock_view.xml",
    ],
    "demo": [],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
}
