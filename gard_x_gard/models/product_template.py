# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_default_uom_pack_id(self):
        uom_pack_id = False
        if self.uom_id:
            uom_pack_id = self.uom_id.id
        else:
            uom_pack_id = self.env["product.uom"].search([], limit=1, order="id").id
        return uom_pack_id

    uom_pack_id = fields.Many2one(
        "product.uom",
        "Package UoM",
        default=_get_default_uom_pack_id,
        required=True,
        help="Package unit of measure.",
    )
    uom_ids = fields.Many2many(
        "product.uom",
        string="Product UoMs",
        compute="_get_product_uom_ids",
        store=True,
        readonly=True,
        index=True,
        help="These are the available units of measure for this product.",
    )

    @api.multi
    @api.depends("uom_po_id", "uom_id", "uom_pack_id")
    def _get_product_uom_ids(self):
        for product in self:
            product.uom_ids = product.uom_po_id + product.uom_id + product.uom_pack_id
