# -*- coding: utf-8 -*-

#import logging

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price Extended'))