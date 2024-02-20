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
        self.env['product.pricelist.item']._compute_uom_ids()
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
        
    def _compute_product_cost(self):
        standard_price = self.standard_price
        valuation = self.stock_value
        qty_available = self.qty_at_date
        
        if qty_available:
            standard_price = valuation / qty_available
    
        return standard_price
        
    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        res = super().price_compute(price_type, uom=False, currency=False, company=False)
        if price_type == 'standard_price':
            if not uom and self._context.get('uom'):
                uom = self.env['product.uom'].browse(self._context['uom'])
            if not currency and self._context.get('currency'):
                currency = self.env['res.currency'].browse(self._context['currency'])
            products = self.with_context(force_company=company and company.id or self._context.get('force_company', self.env.user.company_id.id)).sudo()
            prices = dict.fromkeys(self.ids, 0.0)
            for product in products:
                prices[product.id] = product._compute_product_cost()
                if uom:
                    prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)
                # Convert from current user company currency to asked one
                # This is right cause a field cannot be in more than one currency

                if currency:
                    prices[product.id] = product.currency_id.compute(prices[product.id], currency)

            res = prices
        
        return res
