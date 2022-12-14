# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# _logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    account_analytic_id = fields.Many2one(
        "account.analytic.account", string="Propagate Analytic Account"
    )

    @api.one
    def button_propagate_account_analytic_account(self):
        account_analytic_id = self.account_analytic_id
        for line in self.order_line:
            line['account_analytic_id'] = account_analytic_id
        return True

    def button_order_line_unlink(self):
        for line in self.order_line:
            line.unlink()
        return True
