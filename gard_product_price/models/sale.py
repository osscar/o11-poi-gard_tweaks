# -*- coding: utf-8 -*-
# import logging

# import datetime
from odoo import models, fields, api, _

# _logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_default_pricelist_id(self):
        # _logger.debug('_g_def_p call _context >>>: %s', self._context)
        # _logger.debug('_g_def_p call _context active_ids >>>: %s', self._context.get('params').get('id'))
        _get_order_id = self._context.get("params", {}).get("id")
        if _get_order_id:
            order_id = self.env["sale.order"].search([("id", "=", _get_order_id)])
            return order_id.pricelist_id

    pricelist_item_count = fields.Integer(
        "Pricelist Item Count", compute="_get_count_active_pricelist_items"
    )
    # added pricelist_id field to segment
    # the price_unit computation per order_line
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Sale Order Line Pricelist",
        default=_get_default_pricelist_id,
        required=True,
        help="Pricelist for current sales order line.",
    )
    product_uom_ids = fields.Many2many(
        "product.uom", "Product UoM", compute="_get_product_uom_ids"
    )

    @api.multi
    def _get_count_active_pricelist_items(self):
        for order_line in self:
            product_id = order_line.product_id
            order_line.pricelist_item_ids = product_id.pricelist_item_ids.filtered(
                lambda item: item.active_pricelist == True
            )
            order_line.pricelist_item_count = len(order_line.pricelist_item_ids)

    @api.multi
    def _get_product_uom_ids(self):
        for order_line in self:
            product = order_line.product_id
            order_line["product_uom_ids"] = product.uom_id + product.uom_pack_id

    @api.multi
    def _get_display_price(self, product):
        res = super(SaleOrderLine, self)._get_display_price(product)
        # _logger.debug('_gdp call product >>>: %s', product.default_code)
        # mod'd method to work on order_line rather than the order
        if self.pricelist_id:
            if self.pricelist_id.discount_policy == "with_discount":
                return product.with_context(pricelist=self.pricelist_id.id).price
            product_context = dict(
                self.env.context,
                partner_id=self.order_id.partner_id.id,
                date=self.order_id.date_order,
                uom=self.product_uom.id,
            )
            final_price, rule_id = self.pricelist_id.with_context(
                product_context
            ).get_product_price_rule(
                self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id
            )
            base_price, currency_id = self.with_context(
                product_context
            )._get_real_price_currency(
                product,
                rule_id,
                self.product_uom_qty,
                self.product_uom,
                self.pricelist_id.id,
            )
            if currency_id != self.order_id.pricelist_id.currency_id.id:
                base_price = (
                    self.env["res.currency"]
                    .browse(currency_id)
                    .with_context(product_context)
                    .compute(base_price, self.order_id.pricelist_id.currency_id)
                )
            # force final_price to avoid min_quantity restrictions on super
            return final_price
        # fall back on super if no pricelist_id is set on order_line
        else:
            return res

    # recompute price_unit  onchange pricelist_id
    @api.onchange("pricelist_id")
    @api.multi
    def _onchange_pricelist_id(self):
        # _logger.debug('_pic call self >>>: %s', self)
        # used _product_id_change method as template
        vals = {}
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get("product_uom_qty") or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )
        self._compute_tax_id()
        if self.pricelist_id:
            vals["price_unit"] = self.env[
                "account.tax"
            ]._fix_tax_included_price_company(
                self._get_display_price(product),
                product.taxes_id,
                self.tax_id,
                self.company_id,
            )
        self.update(vals)

    @api.multi
    def button_product_pricelist_items(self):
        product_id = self.product_id.id

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
