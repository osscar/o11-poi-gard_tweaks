# -*- coding: utf-8 -*-
import logging
import datetime
from odoo import models, fields, api, exceptions, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    active_pricelist_item_ids = fields.Many2many(
        'product.pricelist.item',
        'Pricelist Items',
        compute='_get_active_pricelist_items')

    @api.one
    def _get_active_pricelist_items(self):
        self.active_pricelist_item_ids = self.pricelist_item_ids.filtered(
            lambda item: item.active_pricelist == True)

    @api.multi
    def button_product_pricelist_items(self):
        product_id = self.id

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
