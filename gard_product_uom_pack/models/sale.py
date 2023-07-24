# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_uoms = fields.Many2many(
        comodel_name="product.uom",
        related="product_id.uom_ids",
        readonly=True,
    )
    # product_uom = fields.Many2one('product.uom', domain="[('id', 'in', product_uoms)]")

    # def _get_product_uoms(self):
    #     # product_uoms = []
    #     # for line in self:
    #     product_uoms = []
    #     for uom in self.product_id.uom_ids:
    #         product_uoms = uom
    #     _logger.debug("_gpu product_id.uom_ids >>> %s" % self.product_id.uom_ids)
    #     _logger.debug("_gpu product_uoms pre >>> %s" % self.product_uoms)
    #     return product_uoms
    #     _logger.debug("_gpu product_uoms >>> %s" % self.product_uoms)
    #     # return product_uoms

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        _logger.debug("pic product_id pre >>> %s" % self.product_id.display_name)
        _logger.debug("pic product_uoms pre >>> %s" % self.product_uoms)
        # if self.product_id:
        #     self.product_uoms = self._get_product_uoms()
        _logger.debug("pic product_id post >>> %s" % self.product_id.display_name)
        _logger.debug("pic product_uoms post >>> %s" % self.product_uoms)
        _logger.debug("pic res post >>> %s" % res)
        return res
