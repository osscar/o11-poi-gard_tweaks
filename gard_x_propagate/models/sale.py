# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, models, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def button_order_line_unlink(self):
        if self.state != "draft":
            raise ValidationError(
                ("Cannot delete lines if order is not in draft state.")
            )
        for line in self.order_line:
            line.unlink()
        return True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.one
    def button_propagate_route(self):
        if self.order_id.state != "draft":
            raise ValidationError(("Cannot propagate if order is not in draft state."))
        route_id = self.route_id
        for line in self.order_id.order_line:
            line["route_id"] = route_id
        return True

    @api.one
    def button_propagate_pricelist(self):
        if self.order_id.state != "draft":
            raise ValidationError(("Cannot propagate if order is not in draft state."))
        pricelist_id = self.pricelist_id
        for line in self.order_id.order_line.filtered(lambda l: self.id != l.id):
            line["pricelist_id"] = pricelist_id
        return True
