# -*- coding: utf-8 -*-
import datetime
from openerp import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def button_product_pricelist_items(self):
        # get product id
        product_id = self.product_id.id

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
