# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import odoo.addons.decimal_precision as dp

# _logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_factor = fields.Float(
        string="Margin Factor",
        compute="_product_margin_factor",
        digits=dp.get_precision("Product Price"),
        store=True,
    )

    @api.depends(
        "product_id",
        "purchase_price",
        "product_uom_qty",
        "price_unit",
        "price_subtotal",
    )
    def _product_margin_factor(self):
        for line in self:
            # currency = line.order_id.pricelist_id.currency_id
            if line.price_subtotal == 0:
                line.margin_factor = -1
            elif line.purchase_price == 0:
                line.margin_factor = line.price_subtotal
            else:
                line.margin_factor = line.price_subtotal / (
                    line.purchase_price * line.product_uom_qty
                )

    @api.onchange("product_id")
    def check_pricelist(self):
        if self.product_id and not self.order_id.pricelist_id:
            raise ValidationError(
                "Please select a pricelist before selecting a product."
            )
            
    def _compute_margin(self, order_id, product_id, product_uom_id):
        price = super()._compute_margin(order_id, product_id, product_uom_id)
        frm_cur = self.env.user.company_id.currency_id
        to_cur = order_id.pricelist_id.currency_id
        if frm_cur and to_cur:
            stock_value = product_id.stock_value
            qty_at_date = product_id.qty_at_date
            purchase_price = 0.0
            if qty_at_date == 0.0:
                stock_value = product_id.standard_price
                qty_at_date = product_id.immediately_usable_qty
            if qty_at_date != 0.00:
                purchase_price = stock_value / qty_at_date
                if product_uom_id != product_id.uom_id:
                    purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
                ctx = self.env.context.copy()
                ctx['date'] = order_id.date_order
                price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        return price

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        res = super()._get_purchase_price(pricelist, product, product_uom, date)
        qty_at_date = product.qty_at_date
        if qty_at_date == 0.0:
            frm_cur = self.env.user.company_id.currency_id
            to_cur = pricelist.currency_id
            stock_value = product.standard_price
            qty_at_date = product.immediately_usable_qty
            purchase_price = stock_value
            if product_uom != product.uom_id:
                purchase_price = product.uom_id._compute_price(purchase_price, product_uom)
            ctx = self.env.context.copy()
            ctx['date'] = date
            price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
            res = {'purchase_price': price}
        return res
