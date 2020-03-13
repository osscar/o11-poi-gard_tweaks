# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    # group_product_variant = fields.Selection([
    #     (0, "No variants on products"),
    #     (1, 'Products can have several attributes, defining variants (Example: size, color,...)')
    # ], "Product Variants",
    #     help="""Work with product variant allows you to define some variant of the same products
    #             , an ease the product management in the ecommerce for example""",
    #     implied_group='product.group_product_variant')
    # group_sale_pricelist = fields.Boolean("Use pricelists to adapt your price per customers",
    #                                       implied_group='product.group_sale_pricelist',
    #                                       help="""Allows to manage different prices based on rules per category of customers.
    #             Example: 10% for retailers, promotion of 5 EUR on this product, etc.""")
    # group_pricelist_item = fields.Boolean("Show pricelists to customers",
    #                                       implied_group='product.group_pricelist_item')
    # group_product_pricelist = fields.Boolean("Show pricelists On Products",
    #                                          implied_group='product.group_product_pricelist')
    # sale_pricelist_setting = fields.Selection([
    #     ('fixed', 'A single sale price per product'),
    #     ('percentage', 'Specific prices per customer segment, currency, etc.'),
    #     ('formula', 'Advanced pricing based on formulas (discounts, margins, rounding)')
    # ], required=True,
    #     default='formula',
    #     help='Fix Price: all price manage from products sale price.\n'
    #          'Different prices per Customer: you can assign price on buying of minimum quantity in products sale tab.\n'
    #          'Advanced pricing based on formula: You can have all the rights on pricelist')
    # def setUp(self):
    #     self.SaleConfigSettings = self.env['res.config.settings']

    # @api.model
    # def set_pricelist_parameters(self):
    #     _logger.info("> Settings sign-up parameters")
    # settings = self.env['res.config.settings']
    # settings.sale_pricelist_setting = 'formula'

    @api.multi
    def set_values(self):
        _logger.info("> Settings sign-up parameters")
        super(SaleConfiguration, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        ICPSudo.set_param('sale.sale_pricelist_setting', 'formula')
        _logger.info("> ... done.")

    @api.model
    def get_values(self):
        res = super(SaleConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        res.update({
            'sale_pricelist_setting': ICPSudo.get_param('sale.sale_pricelist_setting', default='formula'),
        })
        return res

        # self.env['ir.config_parameter'].set_values(
        #     'sale_pricelist_setting', 'formula')
        # self.execute()

        # sale_pricelist_setting = 'formula'

        # self.env['ir.config_parameter'].set_param(
        #     'sale_pricelist_setting', 'formula')
        # SaleConfigSettings.execute()
        # _logger.info("> ... done.")

    # @api.multi
    # def set_groups(self):
    #     return self.update({
    #         'group_product_pricelist': False,
    #         'group_sale_pricelist': True,
    #         'group_pricelist_item': True,
    #         'group_product_variant': True,
    #     })

    # @api.onchange('sale_pricelist_setting')
    # def _onchange_sale_price(self):
    #     if self.sale_pricelist_setting == 'percentage':
    #         self.update({
    #             'group_product_pricelist': True,
    #             'group_sale_pricelist': True,
    #             'group_pricelist_item': False,
    #         })
    #     elif self.sale_pricelist_setting == 'formula':
    #         self.update({
    #             'group_product_pricelist': False,
    #             'group_sale_pricelist': True,
    #             'group_pricelist_item': True,
    #         })
    #     else:
    #         self.update({
    #             'group_product_pricelist': False,
    #             'group_sale_pricelist': False,
    #             'group_pricelist_item': False,
    #         })
