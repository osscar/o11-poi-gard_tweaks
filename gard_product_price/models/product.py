# -*- coding: utf-8 -*-

import logging

import datetime
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    active_pricelist_item_ids = fields.Many2many(
        'product.pricelist.item',
        'Pricelist Items',
        compute='_get_active_pricelist_items')
    stock_value_unit = fields.Monetary(
        'Unit Stock Value', 
        compute='_compute_value_unit',
        currency_field="currency_id",
        store=True,
        readonly=True,
        help='This is the current computed stock value. Standard price on the other hand, shows the value of the last stock move.')

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
        # self.env['product.pricelist.item']._compute_uoms()
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

    @api.depends('qty_at_date')
    @api.multi
    def _compute_value_unit(self):
        valuation = []
        for product in self:
            valuation = product.stock_value
            qty_available = product.qty_at_date
            if qty_available != 0.0:
                valuation = valuation / qty_available
            product.stock_value_unit = valuation
        _logger.debug("_cpc if valuation >>>: %s", valuation)
