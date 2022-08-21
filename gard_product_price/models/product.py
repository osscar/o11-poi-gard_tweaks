# -*- coding: utf-8 -*-
# import logging

import datetime
from odoo import models, fields, api, exceptions, _

# _logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_default_uom_pack_id(self):
        uom_pack_id = False
        if self.uom_id:
            uom_pack_id = self.uom_id.id
        else:
            uom_pack_id = self.env['product.uom'].search([], limit=1, order='id').id
        return uom_pack_id

    uom_pack_id = fields.Many2one(
        'product.uom', 
        'Package Unit of Measure',
        default=_get_default_uom_pack_id, 
        required=True,
        help="Package Unit of Measure.")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def do_change_standard_price(self, new_price, account_id):
        res = super(ProductProduct, self, new_price, account_id)
        product_pricelist_items = self.env['product.pricelist.item'].search([('id', '=', 'product_id')])
        for prod_pl in product_pricelist_items:
            prod_pl.update({'product_cost': new_price})
        return res
        
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
