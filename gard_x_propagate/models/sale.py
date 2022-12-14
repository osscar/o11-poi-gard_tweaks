# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# _logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # account_analytic_id = fields.Many2one(
    #     "account.analytic.account", string="Propagate Analytic Account"
    # )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Propagate Route",
        domain=[("sale_selectable", "=", True)],
        ondelete="restrict",
    )
    pricelist_id = fields.Many2one(
        'product.pricelist', 
        string='Pricelist', 
        required=True, readonly=True, 
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, 
        help="Propagate pricelist on current sales order.")

    # @api.one
    # def button_propagate_account_analytic_account(self):
    #     route_id = self.account_analytic_id
    #     for line in self.order_line:
    #         line["account_analytic_id"] = account_analytic_id
    #     return True

    @api.one
    def button_propagate_route(self):
        route_id = self.route_id
        for line in self.order_line:
            line["route_id"] = route_id
        return True
    
    api.one
    def button_propagate_pricelist(self):
        pricelist_id = self.pricelist_id
        for line in self.order_line:
            line["pricelist_id"] = pricelist_id
        return True

    def button_order_line_unlink(self):
        for line in self.order_line:
            line.unlink()
        return True
