# -*- coding: utf-8 -*-
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class ProductPricelistVersion(models.Model):
  _inherit = 'product.pricelist.version'

  partner_ids = fields.Many2many(comodel_name='res.partner',
                                 relation='product_pricelist_version_partners_rel',
                                 column1='partner_id',
                                 column2='price_version_id',
                                 string='Partners')


class ProductPricelistItem(models.Model):
  _inherit = 'product.pricelist.item'
  _defaults = {
      'base': 1,
  }

  @api.one
  def _calc_unit_price(self):

    if self.min_quantity != 0.0:
      self.unit_price = self.sale_price / self.min_quantity
    else:
      self.unit_price = 0.00

  active_version = fields.Boolean(related='price_version_id.active',
                                  string="Active",
                                  readonly=True)

  sale_price = fields.Float(string='Sale Price',
                            digits=dp.get_precision('Sale Price'),
                            help='Sale price for current item.')

  unit_price = fields.Float(string='Unit Price',
                            digits=dp.get_precision('Product Price'),
                            compute='_calc_unit_price',
                            help='Unit price for current item.')

  pricelist_currency = fields.Many2one(related='price_version_id.pricelist_id.currency_id',
                                       string="Currency",
                                       readonly=True)

  partner_ids = fields.Many2many(related='price_version_id.partner_ids',
                                 string="Partners",
                                 readonly=True)

  pricelist_type = fields.Selection(related='price_version_id.pricelist_id.type',
                                    string="Pricelist type",
                                    readonly=True)
