# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    margin_factor_avg = fields.Float('Margin Factor', readonly=True, group_operator="avg")

    def _select(self):
        return super(SaleReport, self)._select() + ", (SUM(l.margin / COALESCE (cr.rate, 1.00)) / NULLIF(SUM(l.price_subtotal / COALESCE (cr.rate, 1.00)),0.0)) AS margin_factor_avg"
