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

import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_id = fields.Many2one(index=True)
    qty_available = fields.Float(
        "Available Qty.",
        readonly=True,
    )

    # def _get_warning_msg(self):
    #     warning = {}
    #     if self._context.get("warning") == "zero_div":
    #         warning = {
    #                     "warning": {
    #                         "title": _("Input Error"),
    #                         "message": _(
    #                             "Division by zero cannot be performed. Net sale margin calculation will be set to 0 when product cost is 0."
    #                         ),
    #                     },
    #                 }
    #     elif self._context.get("warning") == "recompute":
    #         warning = {
    #                     "warning": {
    #                         "title": _("Recompute"),
    #                         "message": _(
    #                             "If you continue, all affected pricelist items \
    #                             by the changes made to this record, will be recomputed. \
    #                             This could take a long time depending on the amount of records being processed."
    #                         ),
    #                     },
    #                 }
    #     return warning
        
    @api.model
    def _get_qty_available(self, product):
        qty_available = product.qty_available
        _logger.debug("_gqa qty_available >>>: %s", qty_available)
        if qty_available == 0.0:
            qty_available = product.immediately_usable_qty
            _logger.debug("_gqa if qty_available >>>: %s", qty_available)
        route = self.route_id
        if route.pull_ids:
            # qty_available = 0.0
            location = route.pull_ids[0].location_src_id
            _logger.debug("_gqa route >>>: %s", route)
            quants = self.env["stock.quant"].search([('location_id','=',location.id), ('product_id','=',product.id)])
            _logger.debug("_gqa quants >>>: %s", quants)
            qty_available = sum(q.quantity for q in quants)
            _logger.debug("_gqa qty_available >>>: %s", qty_available)
        return qty_available

    @api.onchange('product_id', 'product_uom', 'route_id')
    def onchange_product_uom_route(self):
        if not self.route_id or not self.product_id or not self.product_uom:
            return
        self.qty_available = self._get_qty_available(self.product_id)
            
    @api.multi
    def button_product_stock_quantity(self):
        product_id = self.product_id.id
        view_id = self.env.ref(
            "gard_product_stock_qty.view_product_stock_quantity_tree"
        ).id

        return {
            "type": "ir.actions.act_window",
            "name": "Product Stock Quantity",
            "res_model": "stock.quant",
            "domain": [
                ("product_id", "=", product_id)
            ],
            "views": [(view_id, "tree")],
            "view_id": view_id,
            "context": {"group_by": ["location_id", "product_id"]},
            "target": "new",
        }
