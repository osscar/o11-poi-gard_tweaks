# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, models, _

# from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _exc_check(self, vals):
        exc_field, exc_field_vals = "state", ["draft", "sent"]
        vals["exc_vals"] = {
            "model": self._context.get("active_model"),
            "field": exc_field,
            "field_rec_vals": [self.state],
            "field_vals": exc_field_vals,
            "msg": vals["exc_msg"],
        }
        _logger.debug('_ec vals >>>: %s', vals)
        _logger.debug('_ec vals[model] >>>: %s', vals["model"])

        exc_obj = self.env["propagate.exception"]
        
        return exc_obj._exception_check(vals)

    def button_unlink_order_line(self):
        # check state
        vals = {
            "exc_msg": "Cannot delete order lines if order is not in draft state.",
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
            "exc_msg": "Cannot propagate route if order is in the following states: ",
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
            "is_exc": self.state not in ("draft", "sent"),
            "exc_msg": "Cannot propagate pricelist if order has been confirmed.",
        }
        self.order_id._exc_check(vals)

        pricelist_id = self.pricelist_id
        for line in self.order_id.order_line.filtered(lambda l: self.id != l.id):
            line["pricelist_id"] = pricelist_id

        return True
