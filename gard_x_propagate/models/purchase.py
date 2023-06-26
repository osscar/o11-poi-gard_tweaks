# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _exc_check(self, vals):
        exc_obj = self.env["propagate.exception"]
        exc_states = {"dra": "Draft", "sent": "Sent", "to_approve": "To Approve",}
        vals[exc_msg] += exc_states
        vals["is_exc"] = self.state not in exc_states
        return exc_obj._exception_check(vals)

    def button_unlink_order_line(self):
        # check state
        vals = {
            "exc_msg": "Can only delete lines if the record is in the folllowing states: ",
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
            "exc_msg": "Cannot propagate analytic account if order is not in draft state.",
        }
        self._exc_check(vals)
        val_states = ["draft"]
        verr_msg = "Cannot propagate analytic account if order is not in draft state."
        self.with_context(val_states=val_states, verr_msg=verr_msg)._check_state()

        account_analytic_id = self.account_analytic_id
        for line in self.order_id.order_line:
            line["account_analytic_id"] = account_analytic_id

        return True
