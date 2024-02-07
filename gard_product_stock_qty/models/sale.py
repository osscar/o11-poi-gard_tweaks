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

    qty_available = fields.Integer(
        "Available Qty.",
        compute="_get_product_qty_available",
    )

    @api.model
    def _get_qty_available(self, product):
        qty_available = product.qty_available
        _logger.debug("_gqa qty_available >>>: %s", qty_available)
        if qty_available == 0.0:
            qty_available = product.immediately_usable_qty
            _logger.debug("_gqa if qty_available >>>: %s", qty_available)
        return qty_available
            
    @api.multi
    def _get_product_qty_available(self):
        for line in self:
            product_id = line.product_id
            _logger.debug("_gqa product_id >>>: %s", product_id)
            # _logger.debug("_gqa line.qty_available >>>: %s", line.qty_available)
            line.qty_available = line._get_qty_available(product_id)
            # _logger.debug("_gqa line.qty_available post >>>: %s", line.qty_available)

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
