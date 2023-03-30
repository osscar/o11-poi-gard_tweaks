# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, exceptions, _


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

    active_item_ids = fields.One2many(
        'product.pricelist.item',
        'product_tmpl_id',
        'Active Pricelist Items',
        domain=[('active_pricelist', '=', True)])

    @api.multi
    def button_product_pricelist_items(self):
        product_id = self.product_variant_id.id

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
