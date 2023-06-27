# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _exc_check(self, vals):
        exc_field, exc_field_vals = "state", ["draft", "sent"]
        vals["exc_vals"] = {
            "model": self._name,
            "field": exc_field,
            "field_rec_vals": [getattr(self, exc_field)],
            "field_vals": exc_field_vals,
            "msg": vals["exc_msg"],
        }

        result = self.env["propagate.exception"]._exception_check(vals)

        return result

    def button_unlink_order_line(self):
        # check state
        vals = {
            "check_type": "state",
            "exc_msg": "Can only delete order lines if order is in the following states: ",
        }
        self._exc_check(vals)

        for line in self.order_line:
            line.unlink()

        return True


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.one
    def button_propagate_account_analytic_account(self):
        # check state
        vals = {
            "check_type": "state",
            "exc_msg": "Can only propagate analytic accounts if order is in the following states: ",
        }
        self._exc_check(vals)

        account_analytic_id = self.account_analytic_id
        for line in self.order_id.order_line:
            line["account_analytic_id"] = account_analytic_id

        return True
