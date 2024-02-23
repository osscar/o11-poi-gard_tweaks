# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import odoo.addons.decimal_precision as dp

# _logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _update_cost_bom(self, product_id):
        bom_obj = self.env['mrp.bom']
        bom = bom_obj._bom_find(product=product_id)
        price = product_id._calc_price(bom)
        # _logger.debug("_ucb bom >>>: %s", bom)
        # _logger.debug("_ucb price >>>: %s", price)
        if price != product_id.standard_price:
            # _logger.debug("_uc      b if standard_price >>>: %s", product_id.standard_price)
            if product_id.categ_id.property_valuation == "manual":
                product_id.standard_price = price
                # _logger.debug("_ucb if standard_price >>>: %s", product_id.standard_price)
        return True
        
    def _compute_margin(self, order_id, product_id, product_uom_id):
        # _logger.debug("_cm standard_price >>>: %s", product_id.standard_price)
        price = super()._compute_margin(order_id, product_id, product_uom_id)
        if product_id.bom_ids:
            self._update_cost_bom(product_id)
            # _logger.debug("_cm if standard_price >>>: %s", product_id.standard_price)
        return price