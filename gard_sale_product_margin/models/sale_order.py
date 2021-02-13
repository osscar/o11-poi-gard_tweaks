# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    margin_factor = fields.Float(string='Margin Factor', compute='_product_margin_factor', digits=dp.get_precision('Product Price'), store=True)

    @api.depends('product_id', 'purchase_price', 'product_uom_qty', 'price_unit', 'price_subtotal')
    def _product_margin_factor(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            if line.price_subtotal == 0:
                line.margin_factor = -1
            elif line.purchase_price == 0:
                line.margin_factor = line.price_subtotal
            else:
                line.margin_factor = line.price_subtotal / (line.purchase_price * line.product_uom_qty)

    @api.onchange('product_id')
    def check_pricelist(self):
        if self.product_id and not self.order_id.pricelist_id:
            raise ValidationError("Please select a pricelist before selecting a product.")
