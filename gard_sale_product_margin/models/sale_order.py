# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_factor = fields.Float(compute='_product_margin_factor', digits=dp.get_precision('Product Price'))

    @api.depends('purchase_price', 'price_unit')
    def _product_margin_factor(self):
        for line in self:
            if line.price_unit == 0:
                line.margin_factor = 1
            else:
                currency = line.order_id.pricelist_id.currency_id
                line.margin_factor = currency.round(line.purchase_price / line.price_unit)

    @api.onchange('product_id')
    def check_pricelist(self):
        if self.product_id and not self.order_id.pricelist_id:
            raise ValidationError("Please select a pricelist before selecting a product.")
