# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, models, _

# _logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super(StockMove, self).onchange_product_id()
        product_id = self.product_id
        if product_id:
            # add domain to product_uom field
            product_uoms = product_id.uom_ids
            res["domain"] = {
                "product_uom": [("id", "in", [uom.id for uom in product_uoms])],
            }
        return res
