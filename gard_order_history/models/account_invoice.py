# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields, api, exceptions, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    payment_ids = fields.Many2many('account.payment',
        'account_invoice_payment_rel', 'invoice_id', 'payment_id',
        string="Payments", copy=False, readonly=True, track_visibility='always')

    residual = fields.Monetary(string='Amount Due',
        compute='_compute_residual', store=True, help="Remaining amount due.",
        track_visibility='always')

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'payment_ids' in init_values and self.payment_ids:
            return 'gard_order_history.mt_payments'
        return super(AccountInvoice, self)._track_subtype(init_values)
