# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _exception_check(self, vals):
        model, exc_field, exc_field_vals, msg = self._name, False, [], vals["exc_msg"]

        check_type = vals["check_type"]
        if check_type == "state":
            exc_field = check_type
            exc_field_vals = ["draft", "sent"]

        # exception check values
        vals["exc_vals"] = {
            "model": model,
            "field": exc_field,
            "field_rec_vals": [getattr(self, exc_field)],
            "field_vals": exc_field_vals,
            "msg": msg,
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


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.one
    def button_propagate_route(self):
        # check state
        vals = {
            "check_type": "state",
            "exc_msg": "Can only propagate route if order is in the following states: ",
        }
        self.order_id._exc_check(vals)

        route_id = self.route_id
        for line in self.order_id.order_line:
            line["route_id"] = route_id

        return True

    @api.one
    def button_propagate_pricelist(self):
        # check state
        vals = {
            "check_type": "state",
            "exc_msg": "Can only propagate pricelist if order is in the following states: ",
        }
        self.order_id._exc_check(vals)

        pricelist_id = self.pricelist_id
        for line in self.order_id.order_line.filtered(lambda l: self.id != l.id):
            line["pricelist_id"] = pricelist_id

        return True
