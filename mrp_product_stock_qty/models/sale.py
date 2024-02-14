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

# import logging

from odoo import fields, models, api

# _logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def button_product_stock_quantity(self):
        res = super().button_product_stock_quantity()
        product_ids = self.product_id
        view_id = self.env.ref(
            "gard_product_stock_qty.view_product_stock_quantity_tree"
        ).id
        search_view_id = False
        domain = [("product_id","=",product_ids.id)]
        context = {"group_by": ["location_id", "product_id"]}
        if product_ids.bom_ids:
            prod_obj = self.env["product.product"]
            product_ids = prod_obj.search([("id","in",[bl.product_id.id for b in self.product_id.bom_ids for bl in b.bom_line_ids])])
            search_view_id = self.env.ref(
            "gard_product_stock_qty.view_product_stock_quantity_search"
        ).id
            domain = [('location_id.usage','=','internal'), ("product_id","in",product_ids.ids)]
            context = {"group_by": ["location_id", "product_id"], "expand": 1}
            res = {
            "type": "ir.actions.act_window",
            "name": "Product Stock Quantity",
            "res_model": "stock.quant",
            "domain": domain,
            "views": [(view_id, "tree")],
            "view_id": view_id,
            "search_view_id": search_view_id,
            "context": context,
            "target": "new",
            }

        return res