# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import fields, models, _

# _logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_uoms = fields.Many2many(
        comodel_name="product.uom",
        related="product_id.uom_ids",
        readonly=True,
    )
