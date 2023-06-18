# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_unlink_order_line(self):
        for line in self.order_line:
            line.unlink()
        return True

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.one
    def button_propagate_account_analytic_account(self):
        if self.order_id.state != "draft":
            raise ValidationError(("Cannot propagate if order is not in draft state."))
        account_analytic_id = self.account_analytic_id
        for line in self.order_id.order_line:
            line["account_analytic_id"] = account_analytic_id
        return True
