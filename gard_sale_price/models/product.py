# -*- coding: utf-8 -*-
import datetime
from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def button_product_pricelist_items(self):
        product_id = self.id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Pricelist Items',
            'res_model': 'product.pricelist.item',
            'domain': [('product_id', '=', product_id),
                       ('active_version', '=', True)],
            'view_id': False,
            'view_mode': 'tree',
            'context': {},
            'target': 'new',
        }

    pricelist_item_ids = fields.One2many('product.pricelist.item',
                                         'product_id',
                                         domain=[('active_version', '=', True),
                                                 ('pricelist_type', '=', 'sale'),
                                                 '|', ('price_version_id.date_end', '=', False),
                                                 ('price_version_id.date_end', '>=', datetime.datetime.now().strftime('%Y-%m-%d'))],
                                         string='Pricelist Items')
