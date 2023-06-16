# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, exceptions, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    active_item_ids = fields.One2many(
        "product.pricelist.item",
        "product_tmpl_id",
        "Active Pricelist Items",
        domain=[("active_pricelist", "=", True)],
    )

    @api.multi
    def button_product_pricelist_items(self):
        product_id = self.product_variant_id.id

        return {
            "name": "Pricelist Items",
            "res_model": "product.product",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_id": self.env.ref(
                "gard_product_price.product_product_prices_view_form"
            ).id,
            "context": {"turn_view_readonly": True},
            "res_id": product_id,
            "target": "new",
        }
