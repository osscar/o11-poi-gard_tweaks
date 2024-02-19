# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields, api, _

import odoo.addons.decimal_precision as dp

# _logger = logging.getLogger(__name__)


class PropagateProduct(models.TransientModel):
    """
    Product propagation wizard.
    """

    _name = "propagate.product"
    _description = "Create order lines with selected products."

    product_ids = fields.Many2many(
        "product.product",
        string="Select Products",
    )
    wizard_line = fields.One2many(
        "propagate.product.line",
        "wizard_id",
        string="Wizard Lines",
        help="These products will be propagated to order lines.",
    )

    def button_create_wizard_line(self):
        for product in self.product_ids:
            line_vals = {
                "wizard_id": self.id,
                "product_id": product.id,
                "name": product.display_name,
                "date_planned": fields.Date.today(),
                "product_qty": 1.0,
                "product_uom": product.uom_id.id,
                "price_unit": 1.0,
            }
            line = self.wizard_line.create(line_vals)
            # line.onchange_product_id()
        return {
            "type": "set_scrollTop",
        }

    @api.one
    def button_create_order_line(self):
        active_model = self._context.get("active_model", False)
        active_ids = self._context.get("active_ids", False)
        order_obj = self.env[active_model]
        order_ids = active_ids
        res = order_obj.browse(order_ids)
        for order in res:
            for line in self.wizard_line:
                # _logger.debug("bcaa order >>>: %s", order)
                if active_model == "purchase.order" or "sale.order":
                    line_obj = order.order_line
                order_line_vals = {
                    "order_id": order.id,
                    "product_id": line.product_id.id,
                    "name": line.name,
                    "date_planned": line.date_planned,
                    "product_qty": line.product_qty,
                    "product_uom": line.product_uom.id,
                    "price_unit": line.price_unit,
                }
                if active_model == "sale.order":
                    order_line_vals["product_uom_qty"] = order_line_vals["product_qty"]
                    del order_line_vals["product_qty"]
                line_obj.create(order_line_vals)
        return {
            "type": "set_scrollTop",
        }

    def button_unlink_product_ids(self):
        self.product_ids = False
        return {
            "type": "set_scrollTop",
        }

    def button_unlink_wizard_line(self):
        for line in self.wizard_line:
            line.unlink()
        return {
            "type": "set_scrollTop",
        }


class PropagateProductLine(models.TransientModel):
    """
    Product propagate wizard line.
    """

    _name = "propagate.product.line"
    _description = "Product propagate wizard lines."
    _rec_name = "name"

    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
    )
    name = fields.Char(string="Name", required=True, help="Order line name.")
    date_planned = fields.Datetime("Date Planned", required=True)
    product_qty = fields.Float(
        string="Quantity",
        required=True,
        default=1.0,
        digits=dp.get_precision("Product Unit of Measure"),
    )
    product_uom = fields.Many2one(
        "product.uom",
        "Quantity Unit of Measure",
        domain=lambda self: self._get_product_uom_domain(),
        help="Product quantity unit of measure.",
    )
    price_unit = fields.Float(
        string="Unit Price", digits=dp.get_precision("Product Price"), default=1.0
    )
    wizard_id = fields.Many2one(
        "propagate.product",
        string="Wizard ID",
    )

    def _get_product_uom_domain(self):
        # add domain to product_uom field
        # res = []
        product_id = self.product_id
        product_uoms = product_id.uom_ids
        res = [("id", "in", [uom.id for uom in product_uoms])]
        return res