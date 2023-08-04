# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import models, fields, api, _

# _logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    product_uom_ids = fields.Many2many(
        comodel_name="product.uom",
        related="product_id.uom_ids",
        readonly=True,
    )
    
    @api.multi
    @api.onchange("product_id")
    def onchange_product_id(self):
        res = super(StockMove, self).onchange_product_id()

        vals = {}
        product_id = self.product_id
        if product_id:
            # add domain to product_uom field
            product_uoms = product_id.uom_ids
            res["domain"] = {
                "product_uom": [('id', 'in', list(set([uom.id for uom in product_uoms])))],
            }
        return res