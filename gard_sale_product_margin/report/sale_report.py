# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    margin_factor = fields.Float('Margin Factor', group_operator="avg")
    purchase_price = fields.Float('Puchase Price')


    def _select(self):
        # return super(SaleReport, self)._select() + ", (SUM(l.price_subtotal / COALESCE(cr.rate, 1.0)) / NULLIF(SUM(l.purchase_price / COALESCE(cr.rate, 1.0) * l.product_uom_qty / u.factor * u2.factor),0)) AS margin_factor"
        return super(SaleReport, self)._select() + ", AVG(l.margin_factor) AS margin_factor" + ", SUM(l.purchase_price * l.product_uom_qty / u.factor * u2.factor) AS purchase_price"
