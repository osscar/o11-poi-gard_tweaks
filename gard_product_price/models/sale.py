# -*- coding: utf-8 -*-
# import logging

# import datetime
from odoo import models, fields, api, _

# _logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_default_pricelist_id(self):
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
    product_cost_base = fields.Monetary(
        string="Base Price",
        default=0.0,
        currency_field="currency_id",
        help="Cost price per default product UoM, based on product's Standard Price (when set) or inventory valuation.",
        track_visibility="onchange",
    )

    @api.multi
    def _get_count_active_pricelist_items(self):
        for order_line in self:
            product_id = order_line.product_id
            order_line.pricelist_item_ids = product_id.pricelist_item_ids.filtered(
                lambda item: item.active_pricelist == True
            )
            order_line.pricelist_item_count = len(order_line.pricelist_item_ids)

    def _compute_product_cost(self, order_id, product_id, product_uom_id):
        frm_cur = self.env.user.company_id.currency_id
        to_cur = order_id.pricelist_id.currency_id

        partner_id = self.order_id.partner_id
        date = self.order_id.date_order
        qty = self.product_uom_qty
        uom = self.product_uom
        pricelist = self.pricelist_id

        product_context = dict(
            self.env.context, partner_id=partner_id.id, date=date, uom=uom.id
        )
        final_price, rule_id = pricelist.with_context(
            product_context
        ).get_product_price_rule(product_id, qty or 1.0, partner_id)
        
        rule = self.env["product.pricelist.item"].browse(rule_id)
        product_cost_base = rule.product_cost_base

        if product_uom_id != product_id.uom_id:
            product_cost_base = product_id.uom_id._compute_price(
                product_cost_base, product_uom_id
            )
            
        ctx = self.env.context.copy()
        ctx["date"] = order_id.date_order
        price = frm_cur.with_context(ctx).compute(
            product_cost_base, to_cur, round=False
        )
        
        return price

    @api.multi
    def _get_display_price(self, product):
        # _logger.debug("_gdp self >>>: %s", self)
        pricelist = self.pricelist_id
        if not pricelist:
            return super()._get_display_price(product)
        
        partner_id = self.order_id.partner_id
        date = self.order_id.date_order
        qty = self.product_uom_qty
        uom = self.product_uom
        product_context = dict(
            self.env.context, partner_id=partner_id.id, date=date, uom=uom.id
        )
        
        final_price, rule_id = pricelist.with_context(
            product_context
        ).get_product_price_rule(product, qty or 1.0, partner_id)

        if pricelist.discount_policy == "with_discount":
            return product.with_context(pricelist=pricelist.id).price
        base_price, currency_id = self.with_context(
            product_context
        )._get_real_price_currency(product, rule_id, qty, uom, pricelist.id)
        if currency_id != pricelist.currency_id.id:
            base_price = (
                self.env["res.currency"]
                .browse(currency_id)
                .with_context(product_context)
                .compute(base_price, pricelist.currency_id)
            )
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.onchange("pricelist_id")
    @api.multi
    def _onchange_pricelist_id(self):
        # used _product_id_change method as template
        vals = {}

        date = self.order_id.date_order
        quantity = vals.get("product_uom_qty") or self.product_uom_qty
        partner = self.order_id.partner_id
        lang = False

        if partner:
            lang = partner.lang
        pricelist = self.pricelist_id
        uom = self.product_uom
        tax_id = self.tax_id
        product = self.product_id
        company_id = self.company_id

        product_context = dict(
            self.env.context,
            lang=lang,
            partner=partner,
            quantity=quantity,
            date=date,
            pricelist=pricelist.id,
            uom=uom.id,
        )

        product = product.with_context(product_context)

        self._compute_tax_id()

        if pricelist:
            vals["price_unit"] = self.env[
                "account.tax"
            ]._fix_tax_included_price_company(
                self._get_display_price(product),
                product.taxes_id,
                tax_id,
                company_id,
            )
            vals["product_cost_base"] = self._compute_product_cost(
                self.order_id, self.product_id, self.product_uom
            )

        self.update(vals)

    @api.depends("margin")
    def _product_margin(self):
        super()._product_margin()
        for line in self:
            price = line.product_cost_base
            currency = line.order_id.pricelist_id.currency_id
            line.margin = currency.round(
                line.price_subtotal - (price * line.product_uom_qty)
            )
            if price != 0.0:
                # TO DO: rev functionality wo taxes applied
                line.margin_factor = line.price_subtotal / (
                    price * line.product_uom_qty
                )

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
