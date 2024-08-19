# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_factor = fields.Float(
        string="Margin Factor",
        compute="_product_margin",
        digits=dp.get_precision("Product Price"),
        store=True,
    )

    def _compute_margin(self, order_id, product_id, product_uom_id):
        _logger.debug("_cm self._context >>>: %s", self._context)
        price = 0.0
        try:
            order_id = self._context["item_id"]
        except:
            price = super()._compute_margin(order_id, product_id, product_uom_id)
        frm_cur = self.env.user.company_id.currency_id
        to_cur = order_id.pricelist_id.currency_id
        purchase_price = product_id.standard_price
        if product_uom_id != product_id.uom_id:
            purchase_price = product_id.uom_id._compute_price(purchase_price, product_uom_id)
        ctx = self.env.context.copy()
        try:
            ctx['date'] = fields.Date.today()
            price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        except:
            ctx['date'] = order_id.date_order
        
        return price

    # add route_id to onchange fields
    @api.onchange('product_id', 'product_uom', 'route_id', 'pricelist_id')
    def product_id_change_margin(self):
        _logger.debug("_picm self >>>: %s", self.pricelist_id)
        return super().product_id_change_margin()

    @api.depends("margin")
    def _product_margin(self):
        super()._product_margin()
        for line in self:
            price = line.purchase_price
            _logger.debug("_pm price >>>: %s", price)
            currency = line.order_id.pricelist_id.currency_id
            line.margin = currency.round(line.price_subtotal - (price * line.product_uom_qty))
            if price != 0.0:
                line.margin_factor = line.price_subtotal / (price * line.product_uom_qty)
        # return res

    @api.onchange("product_id")
    def check_pricelist(self):
        if self.product_id and not self.order_id.pricelist_id:
            raise ValidationError(
                "Please select a pricelist before selecting a product."
            )