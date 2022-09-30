# -*- coding: utf-8 -*-

# import logging

from odoo import api, fields, models
from datetime import datetime

from odoo.tools.translate import _
from odoo.http import request
# from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class Import(models.TransientModel):

    _inherit = 'base_import.import'
    
    # inherit csv import do method to write date_update when importing
    # pricelist to cascade on realted base_pricelist_id
    # triggered by depends fields
    @api.multi
    def do(self, fields, options, dryrun=False):
        # self.ensure_one()
        # _logger.debug('do call self >>>: %s', self)
        # _logger.debug('do call res_model >>>: %s', self.res_model)
        # _logger.debug('do call fields >>>: %s', fields)
        # _logger.debug('do call options >>>: %s', options)
        res = super(Import, self).do(fields, options, dryrun)      
        res_model = self.res_model
        # this list unfortunately needs to be updated manually 
        # when updating depends on pl_item _calc_price_unit method
        pl_item_comp_fields = [
            'applied_on',
            'product_tmpl_id',
            'product_id',
            'base',
            'base_pricelist_id',
            'compute_price',
            'percent_price',
            'min_quantity',
            'date_update',
            'uom_pack_id'
        ]
        if res_model == 'product.pricelist.item' and any(fields in pl_item_comp_fields for fields in fields):
            data, import_fields = self._convert_import_data(fields, options)
            for line in data:
                recompute_items = []
                product = False
                extid_2_id = self.env.ref(line[0]).ids
                # _logger.debug('do call line extid_2_id >>>: %s', extid_2_id)
                item_ids = self.env[res_model].search([('id', '=', extid_2_id)])
                for item in item_ids:
                    # _logger.debug('for item call item >>>: %s', item)
                    if item.applied_on == '1_product':
                        product = item.product_tmpl_id
                    if item.applied_on == '0_product_variant':
                        product = item.product_id
                    # _logger.debug('for item call product >>>: %s', product)
                if product:
                    rel_item_ids = item_ids.search(['|', ('product_tmpl_id', '=', product.id), ('product_id', '=', product.id)])
                    recompute_items = rel_item_ids
                    if recompute_items:
                        for r_item in recompute_items:
                            # _logger.debug('write call r_item >>>: %s', r_item)
                            r_item.write({'date_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
        return res