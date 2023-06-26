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
        return exc_obj.with_context(ctx=params)._exception_check()

    def button_unlink_order_line(self):
        # check state
        context = {
            "exc_field": "self.state",
            "exc_vals": "['draft', None]",
            "exc_msg": "Cannot delete order lines if order is not in draft state.",
        }
        self.with_context(ctx=context)._exc_check()

        for line in self.order_line:
            line.unlink()

        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.one
    def button_propagate_route(self):
        # check state
        params = {
            "exc_field": "self.order_id.state",
            "exc_vals": "('draft', None)",
            "exc_msg": "Cannot propagate route if order is not in draft state.",
        }
        self.order_id._exc_check(params)

        route_id = self.route_id
        for line in self.order_id.order_line:
            line["route_id"] = route_id

        return True

    @api.one
    def button_propagate_pricelist(self):
        # check state
        verr_msg = "Cannot propagate pricelist if order is not in draft state."
        val_states = ["draft"]
        self.with_context(verr_msg=verr_msg, val_states=val_states)._check_state()

        pricelist_id = self.pricelist_id
        for line in self.order_id.order_line.filtered(lambda l: self.id != l.id):
            line["pricelist_id"] = pricelist_id

        return True
