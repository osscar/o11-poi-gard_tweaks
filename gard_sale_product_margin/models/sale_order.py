# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import odoo.addons.decimal_precision as dp


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
            currency = line.order_id.pricelist_id.currency_id
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

    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        res = super(SaleOrder, self)._get_purchase_price(
            pricelist, product, product_uom, date
        )
        # frm_cur = self.env.user.company_id.currency_id
        # to_cur = pricelist.currency_id
        purchase_price = product.stock_value / product.qty_at_date
        # if product_uom != product.uom_id:
        #     purchase_price = product.uom_id._compute_price(purchase_price, product_uom)
        # ctx = self.env.context.copy()
        # ctx['date'] = date
        # price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        return res
