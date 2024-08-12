# -*- coding: utf-8 -*-

#import logging

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp

from odoo.exceptions import ValidationError

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    price_unit = fields.Float(digits=dp.get_precision('Product Price Extended'))