# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    partner_ids = fields.Many2many(
        'res.partner',
        # 'product_pricelist_partners_rel', 'partner_id',
        # 'pricelist_id',
        string='Partners')

    item_product_default_code = fields.Char(
        related='item_ids.product_default_code',
        string="Product Internal Reference",
        help='Product default code.', readonly=True)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    _defaults = {
        'base': 1,
    }

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if 'product_default_code' in groupby:
            fields.remove('min_quantity')
            fields.remove('sale_price')
            fields.remove('unit_price')
        return super(
            ProductPricelistItem, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)

    @api.depends('sale_price', 'min_quantity')
    def _calc_unit_price(self):
        if self.min_quantity > 0:
            self.unit_price = self.sale_price / self.min_quantity
        else:
            self.min_quantity = 1
            return {
                'warning': {'title': _('Input Error'),
                            'message': _('Minimum quantity may not be 0. Setting minimum quantity to 1. Please change accordingly.'), },
            }

    # @api.onchange('sale_price', 'min_quantity')
    # def onchange_price(self):
    #     if self.min_quantity > 0:
    #         self.unit_price = self.sale_price / self.min_quantity
    #     else:
    #         self.min_quantity = 1
    #         return {
    #             'warning': {'title': _('Input Error'),
    #                         'message': _('Minimum quantity may not be 0. Setting minimum quantity to 1. Please change accordingly.'), },
    #         }

    active_pricelist = fields.Boolean(
        related='pricelist_id.active', string="Active", readonly=True)

    product_default_code = fields.Char(
        related='product_id.default_code',
        string="Product Internal Reference",
        help='Product default code.',
        readonly=True, store=True)

    sale_price = fields.Monetary(
        string='Sale Price', currency_field='currency_id',
        # digits=dp.get_precision('Sale Price'),
        help='Sale price for current item.')

    unit_price = fields.Monetary(
        string='Unit Price', currency_field='currency_id',
        # digits=dp.get_precision('Product Price'), readonly=True,
        compute='_calc_unit_price',
        readonly=True,
        store=True,
        help='Unit price for current item.')

    partner_ids = fields.Many2many(
        related='pricelist_id.partner_ids', string="Partners",
        readonly=True)

    # pricelist_type = fields.Selection(
    #     related='pricelist_id.type', string="Pricelist type", readonly=True)
