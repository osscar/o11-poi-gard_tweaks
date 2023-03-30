# -*- coding: utf-8 -*-
# import logging

import datetime
from odoo import models, fields, api, exceptions, _

# _logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    active_pricelist_item_ids = fields.Many2many(
        'product.pricelist.item',
        'Pricelist Items',
        compute='_get_active_pricelist_items')

    @api.one
    def _get_active_pricelist_items(self):
        pricelist_item_ids = self.pricelist_item_ids.filtered(
            lambda item: item.active_pricelist and not item.is_hidden)
        pricelist_item_ids += self.env['product.pricelist.item'].search(
            [('applied_on', '=', '3_global')]).filtered(
            lambda item: item.active_pricelist and not item.is_hidden)
        self.active_pricelist_item_ids = pricelist_item_ids

    @api.multi
    def button_product_pricelist_items(self):
        product_id = self.id
        self.env['product.pricelist.item']._compute_uom_pack_id()
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
