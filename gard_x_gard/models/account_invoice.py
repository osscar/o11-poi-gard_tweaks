# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, vals):
        model = request.params.get('model')
        method = request.params.get('method')
        action_invoice_open = method in 'action_invoice_open'
        action_validate_invoice_payment = method in 'action_validate_invoice_payment'
        invoice_refund = method in 'invoice_refund'
        move_reconcile = method in ('assign_outstanding_credit', 'remove_move_reconcile')
        payment_post = model in 'account.payment' and method in 'post'
        send_mail_action = model in 'mail.compose.message' and method in 'send_mail_action'
        # _logger.debug('payment_post funct >>>: %s', model, method)
        _logger.debug('send mail funct >>>: %s', send_mail_action)
        _logger.debug('payment_post >>>: %s' % payment_post)
        group_account_edit = self.env.user.has_group('gard_x_gard.group_account_edit')
        allow_write = action_validate_invoice_payment or action_invoice_open or invoice_refund or move_reconcile or payment_post or group_account_edit or send_mail_action
        _logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        _logger.debug('Allow invoice_refund method: %s', invoice_refund)
        _logger.debug('Allow move_reconcile method: %s', move_reconcile)
        _logger.debug('Allow write: %s', allow_write)
        _logger.debug('state >>>>: %s', self.mapped('state'))
        if any(state != 'draft' for state in set(self.mapped('state')) if allow_write == False):
            raise UserError(_('Edit allowed only in draft state. [%s.%s]' % (request.params.get('model'), request.params.get('method'))))
        else:
            return super().write(vals)
            _logger.info('Written vals: %s', vals)
