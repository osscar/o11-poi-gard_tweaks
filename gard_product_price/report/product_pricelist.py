# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, models
from odoo.tools import float_round

_logger = logging.getLogger(__name__)


class report_product_pricelist(models.AbstractModel):
    _name = 'report.gard_product_price.report_pricelist'

    @api.model
    def get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        pricelist = self.env['product.pricelist'].browse(data.get('form', {}).get('price_list', False))
        products = self.env['product.product'].browse(data.get('ids', data.get('active_ids')))
        # quantities = self._get_quantity(data)
        return {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': 'product.pricelist',
            'docs': products,
            'data': dict(
                data,
                pricelist=pricelist,
                # quantities=quantities,
                pricelist_data=self._get_pricelist_data(pricelist, products)
            ),
        }

    def _get_pricelist_data(self, pricelist, products):
        pricelist_data = []
        pricelist_items = [item for item in pricelist.item_ids if item.product_id in products or item.applied_on == 'global']
        _logger.debug('pricelist items init >>>: %s', pricelist_items)
        # items = []
        # item_vals = {'product': None, 'min_quantity': None, 'price_unit': None, 'price_uom_unit': None, 'price_pack': None, 'proce_uom_pack': None}
        
        # res = {}
        # pricelist_items = [{} for item in pricelist_items]
        for item in pricelist_items:
            items_data = {}
            # product_items
            if item.applied_on == '0_product_variant':
                items_data.setdefault(item.id, {})
                _logger.debug('pricelist items_data item result >>>: %s', items_data)
                items_data[item.id]['product'] = item.product_id.name
                items_data[item.id]['min_quantity'] = item.min_quantity
                items_data[item.id]['price_unit'] = item.price_unit
                items_data[item.id]['price_uom_unit'] = item.product_id.uom_id.name
                items_data[item.id]['price_pack'] = item.price_pack
                items_data[item.id]['price_uom_pack'] = item.product_uom_pack.name
            # global_items
            elif item.applied_on == '3_global':
                _logger.debug('if global_items item >>>: %s', item)
            #     _logger.debug('if global_items item >>>: %s', product)
            #     # _logger.debug('if global_items product_id >>>: %s', item.product_id)
            #     items = item
                items_data[item.id] = products.name
                items_data[item.id]['min_quantity'] = item.min_quantity
                items_data[item.id]['price_unit'] = self._get_price(pricelist, products, qty=min_quantities)
                items_data[item.id]['price_uom_unit'] = product.uom_id
                qty_pack = products.uom_pack_id.factor_inv
                items_data[item.id]['price_pack'] = self._get_price(pricelist, products, qty=qty_pack)
                items_data[item.id]['price_uom_pack'] = products.uom_pack_id
            #     _logger.debug('if global_items min_quantities >>>: %s', min_quantities)
            #     _logger.debug('if global_items uom_prices_pack >>>: %s', uom_prices_pack)
    #         # append product data
            # pricelist_data = [items for items in items_data]
            pricelist_data.append({
                'items_data': items_data,
            #     'item_vals': item_vals,
            #     # 'items_product': items_product,
            #     # 'min_quantities': min_quantities,
            #     # 'prices_unit': prices_unit,
            #     # 'uom_prices_unit': uom_prices_unit,
            #     # 'prices_pack': prices_pack,
            #     # 'uom_prices_pack': uom_prices_pack,
            })
            _logger.debug('pricelist items append >>>: %s', pricelist_items)
            _logger.debug('pricelist items append >>>: %s', items_data)
            _logger.debug('pricelist items append item:vals>>>: %s', pricelist_data)
        # product_items = 
        # pricelist_data = pricelist_items
        return pricelist_data

    def _get_price(self, pricelist, product, qty):
        sale_price_digits = self.env['decimal.precision'].precision_get('Product Price')
        price = pricelist.get_product_price(product, qty, False)
        if not price:
            price = product.list_price
        return float_round(price, precision_digits=sale_price_digits)
