# -*- coding: utf-8 -*-
import logging

import datetime
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_ids = fields.Many2many('account.invoice', string='Invoices', compute='_get_invoiced',
        copy=False, readonly=True, track_visibility='onchange')
    invoice_payment_ids = fields.Many2many('account.payment', string='Invoice Payments', compute='_get_invoice_payments',
        copy=False, readonly=True, track_visibility='onchange')

    @api.multi
    @api.depends('invoice_ids')
    def _get_invoice_payments(self):
        for order in self:
            if order.invoice_ids:
                order.invoice_payment_ids = order.mapped('invoice_ids').mapped('payment_ids')
                _logger.debug('>>>>: %s', (order.invoice_payment_ids))

