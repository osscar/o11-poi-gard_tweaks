# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _update_cost_bom(self, product_id):
        bom_obj = self.env['mrp.bom']
        bom = bom_obj._bom_find(product=product_id)
        price = product_id._calc_price(bom)
        _logger.debug("_ucb bom >>>: %s", bom)
        _logger.debug("_ucb price >>>: %s", price)
        if price != product_id.standard_price:
            _logger.debug("_ucb if standard_price >>>: %s", product_id.standard_price)
            if product_id.category_id.property_valuation == "manual":
                product_id.standard_price = price
                _logger.debug("_ucb if standard_price >>>: %s", product_id.standard_price)
        return True
        
    def _compute_margin(self, order_id, product_id, product_uom_id):
        _logger.debug("_cm standard_price >>>: %s", product_id.standard_price)
        price = super()._compute_margin(order_id, product_id, product_uom_id)
        if product_id.bom_ids:
            self._update_cost_bom(product_id)
            _logger.debug("_cm if standard_price >>>: %s", product_id.standard_price)
        return price

    # @api.model
    # def _get_purchase_price(self, pricelist, product, product_uom, date):
    #     _logger.debug("_gpp product >>>: %s", product)
    #     # qty_at_date = product.immediate_
    #     return super().with_context(qty_at_date=)._get_purchase_price(
    #         pricelist, product, product_uom, date
    #     )
        # if product.bom_ids:
        #     frm_cur = self.env.user.company_id.currency_id
        #     to_cur = pricelist.currency_id
        #     purchase_price = product.standard_price / product.qty_at_date
        #     _logger.debug("_gpp if purchase_price >>>: %s", purchase_price)
        #     if product_uom != product.uom_id:
        #         purchase_price = product.uom_id._compute_price(purchase_price, product_uom)
        #     ctx = self.env.context.copy()
        #     ctx['date'] = date
        #     price = frm_cur.with_context(ctx).compute(purchase_price, to_cur, round=False)
        #     res = {'purchase_price': price}
        # return res