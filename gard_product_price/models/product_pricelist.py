# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    partner_ids = fields.Many2many(
        'res.partner',
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
        if 'product_default_code' or 'product_id' or 'product_tmpl_id' in groupby:
            fields.remove('min_quantity')
            fields.remove('sale_price')
            fields.remove('unit_price')
            fields.remove('net_sale_margin')
            fields.remove('sale_margin_excl')
            fields.remove('product_cost')
        return super(
            ProductPricelistItem, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)

    @api.depends('sale_price', 'min_quantity')
    def _calc_unit_price(self):
        for item in self:
            if item.min_quantity > 0:
                item.unit_price = item.sale_price / item.min_quantity
            else:
                item.min_quantity = 1
                return {
                    'warning': {'title': _('Input Error'),
                                'message': _('Minimum quantity may not be 0. Setting minimum quantity to 1. Please change accordingly.'), },
                }

    @api.one
    @api.depends('sale_price', 'sale_margin_excl', 'min_quantity')
    def _calc_net_sale_margin(self):
        if self.product_cost > 0:
            self.net_sale_margin = (
                (self.unit_price * self.sale_margin_excl) / self.product_cost) - 1
        else:
            self.net_sale_magin = 0
            return {
                'warning': {'title': _('Input Error'),
                            'message': _('Product cost may not be 0. Please update product cost.'), },
            }

    @api.one
    @api.constrains('sale_margin_excl')
    def _check_margin_exclusion_percent(self):
        if self.sale_margin_excl == 0 or self.sale_margin_excl > 1:
            raise ValidationError(
                "Sale margin exclusion must be greater than 0 and less than 1.")

    active_pricelist = fields.Boolean(
        related='pricelist_id.active',
        string="Active",
        readonly=True)

    product_default_code = fields.Char(
        related='product_id.default_code',
        string="Product Code",
        help='Product default code.',
        readonly=True, store=True)

    description = fields.Char(
        string='Description',
        help='Pricelist item description.')

    sale_price = fields.Monetary(
        string='Sale Price',
        currency_field='currency_id',
        help='Sale price for current item.')

    unit_price = fields.Monetary(
        string='Unit Price',
        currency_field='currency_id',
        compute='_calc_unit_price',
        readonly=True,
        store=True,
        help='Unit price for current item.')

    net_sale_margin = fields.Float(
        string='Net Sale Margin',
        compute='_calc_net_sale_margin',
        readonly=True,
        help='Net sale margin for current item (factored with sale margin exclusion).')

    product_cost = fields.Float(
        related='product_id.standard_price',
        string="Product Cost",
        readonly=True,
        help='Cost price based on product\'s Standard Price.')

    sale_margin_excl = fields.Float(
        string='% Excl.',
        default=1.00,
        help='Sale margin exclusion percent (in decimal form). Specify a value between greater than 0 and less than 1.')

    partner_ids = fields.Many2many(
        related='pricelist_id.partner_ids',
        string="Partners")
