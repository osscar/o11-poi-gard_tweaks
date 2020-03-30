# -*- coding: utf-8 -*-
import logging
import datetime
from odoo import models, fields, api, exceptions, _

# _logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pricelist_item_count = fields.Integer(
        "Pricelist Item Count", compute='_get_count_active_pricelist_items')

    @api.one
    def _get_count_active_pricelist_items(self):
        for order_line in self:
            product_id = order_line.product_id
            order_line.pricelist_item_ids = product_id.pricelist_item_ids.filtered(
                lambda item: item.active_pricelist == True)
            order_line.pricelist_item_count = len(
                order_line.pricelist_item_ids)

    @api.multi
    def button_product_pricelist_items(self):
        product_id = self.product_id.id

        return {
            'name': 'Pricelist Items',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('gard_product_price.product_product_prices_view_form').id,
            'context': {'turn_view_readonly': True},
            'res_id': product_id,
            'target': 'new',
        }
