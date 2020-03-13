# -*- coding: utf-8 -*-
import logging
import json
import datetime
from odoo import models, fields, api, exceptions, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # @api.multi
    # def button_product_pricelist_items(self):
    #     product_id = self.id

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Pricelist Items',
    #         'res_model': 'product.pricelist.item',
    #         'domain': [('product_id', '=', product_id),
    #                    ('active_pricelist', '=', True)],
    #         'view_id': False,
    #         'view_mode': 'tree',
    #         'context': {},
    #         'target': 'new',
    #     }

    @api.one
    def _get_product_prices_info_JSON(self):
        _logger = logging.getLogger(__name__)
        # self.payments_widget = json.dumps(False)
        items = self.pricelist_item_ids
        context = dict(self._context or {})
        ret = []

        for item in items:
            ret_item = {
                'id': item.id,
                'product_id': item.product_id,
                'product_tmpl_id': item.product_tmpl_id,
                'min_quantity': item.min_quantity,
                'sale_price': item.sale_price,
                'unit_price:': item.unit_price,
                'pricelist_id': item.pricelist_id,
                'partner_ids': item.partner_ids,
            }
            ret.append(ret_line)
        return ret




    product_prices_widget = fields.Text(
        compute='_get_product_prices_info_JSON')

    @api.multi
    def get_pricelist_items(self):
        """ Open xml view specified in xml_id for current product """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id(
                'gard_sale_price_js', xml_id)
            res.update(
                domain=[('product_id', '=',
                         self.id),
                        ('active_pricelist', '=', True)]
                # , '|',
                # ('date_end', '=', []),
                # ('date_end', '>=',
                #  datetime.datetime.now().strftime('%Y-%m-%d'))]
            )
            return res
        return False
