# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# _logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        product_id = self.product_id
        if product_id:
            # add domain to product_uom field
            product_uoms = product_id.uom_ids
            res["domain"] = {
                "product_uom": [("id", "in", [uom.id for uom in product_uoms])],
            }
        return res