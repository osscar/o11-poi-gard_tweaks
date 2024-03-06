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
        compute="_product_margin_factor",
        digits=dp.get_precision("Product Price"),
        store=True,
    )

    # def _get_warning_msg(self):
    #     warning = {}
    #     if self._context.get("warning") == "zero_div":
    #         warning = {
    #                     "warning": {
    #                         "title": _("Input Error"),
    #                         "message": _(
    #                             "Division by zero cannot be performed. Net sale margin calculation will be set to 0 when product cost is 0."
    #                         ),
    #                     },
    #                 }
    #     elif self._context.get("warning") == "recompute":
    #         warning = {
    #                     "warning": {
    #                         "title": _("Recompute"),
    #                         "message": _(
    #                             "If you continue, all affected pricelist items \
    #                             by the changes made to this record, will be recomputed. \
    #                             This could take a long time depending on the amount of records being processed."
    #                         ),
    #                     },
    #                 }
    #     return warning
    
    def _get_stock_value(self, pricelist, product, product_uom, date):
        purchase_price = 0.0
        frm_cur = self.env.user.company_id.currency_id
        to_cur = pricelist.currency_id
        stock_value = product.stock_value
        qty_at_date = product.qty_at_date
        if product.standard_price != 0:
            stock_value = product.standard_price
            qty_at_date = 1.0
        _logger.debug("_gsv self >>>: %s", self)
        _logger.debug("_gsv qty_at_date >>>: %s", qty_at_date)
        if qty_at_date == 0.0:
            stock_value = product.standard_price
            qty_at_date = product.immediately_usable_qty
            _logger.debug("_gsv if qty_at_date >>>: %s", qty_at_date)
            _logger.debug("_gsv if stock_value >>>: %s", stock_value)
        purchase_price = stock_value / qty_at_date
        if product_uom != product.uom_id:
            purchase_price = product.uom_id._compute_price(purchase_price, product_uom)
        ctx = self.env.context.copy()
        ctx['date'] = date
        price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        return price
            
    @api.model
    def _get_purchase_price(self, pricelist, product, product_uom, date):
        price = super()._get_purchase_price(pricelist, product, product_uom, date)
        if pricelist:
            price = self._get_stock_value(pricelist, product, product_uom, date)
            _logger.debug("_gpp if price >>>: %s", price)
        price = {'purchase_price': price}
        return price
    
    def _compute_margin(self, order_id, product_id, product_uom_id):
        pricelist_id = self.env['product.pricelist'].search([('id','=',self._context.get('pricelist'))])
        _logger.debug("_cm pricelist >>>: %s", pricelist_id)
        date = order_id.date_order
        price = self._get_stock_value(pricelist_id, product_id, product_uom_id, date)
        if not pricelist_id:
            price = super()._compute_margin(order_id, product_id, product_uom_id)
        return price

    @api.onchange('product_id', 'product_uom', 'route_id', 'pricelist_id')
    def product_id_change_margin(self):
        _logger.debug("_picm self >>>: %s", self.order_id.pricelist_id)
        _logger.debug("_picm self >>>: %s", self.pricelist_id)
        return super().product_id_change_margin()
    
    @api.depends(
        "margin",
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

    # @api.onchange('qty_available')
    # def product_id_change_margin(self):
    #     res = super().product_id_change_margin
    #     _logger.debug("prod_chg_mrg self >>>: %s", self)
    #     _logger.debug("prod_chg_mrg res >>>: %s", res)
    #     _logger.debug("prod_chg_mrg self.route_id >>>: %s", self.route_id)
    #     if self.route_id:
    #         _logger.debug("prod_chg_mrg self.route_id >>>: %s", self.route_id)
    #         _logger.debug("prod_chg_mrg self.purchase_price pre >>>: %s", self.purchase_price)
    #         self.purchase_price = self._compute_margin(self.order_id, self.product_id, self.product_uom)
    #         _logger.debug("prod_chg_mrg self.purchase_price post >>>: %s", self.purchase_price)