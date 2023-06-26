# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, models, _

# from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _exc_check(self, params):
        exc_obj = self.env["propagate.exception"]
        exc_state_keys = ["id", "name"]
        exc_state_ids = ["draft", "sent"]
        exc_state_names = [rs for s in exc_state_ids for rs in self.search(['id', '=', s])]
        exc_states = {es[0]: list(esi[1:]) for esi in zip(exc_states, exc_state_names)}
        params[exc_state_names] = exc_state_names

        params["is_exc"] = self.state not in tuple(s for s in exc_states)
        return exc_obj._exception_check(params)

    def button_unlink_order_line(self):
        # check state
        params = {
            "exc_msg": "Cannot delete order lines if order is not in draft state.",
        }
        self._exc_check(params)

        for line in self.order_line:
            line.unlink()

        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.one
    def button_propagate_route(self):
        # check state
        params = {
            "exc_msg": "Cannot propagate route if order has been confirmed.",
        }
        self.order_id._exc_check(params)

        route_id = self.route_id
        for line in self.order_id.order_line:
            line["route_id"] = route_id

        return True

    @api.one
    def button_propagate_pricelist(self):
        # check state
        params = {
            "is_exc": self.state not in ("draft", "sent"),
            "exc_msg": "Cannot propagate pricelist if order has been confirmed.",
        }
        self.order_id._exc_check(params)

        pricelist_id = self.pricelist_id
        for line in self.order_id.order_line.filtered(lambda l: self.id != l.id):
            line["pricelist_id"] = pricelist_id

        return True
