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
        action_invoice_open = request.params.get('method') in 'action_invoice_open'
        action_validate_invoice_payment = request.params.get('method') in 'action_validate_invoice_payment'
        invoice_refund = request.params.get('method') in 'invoice_refund'
        move_reconcile = request.params.get('method') in ('assign_outstanding_credit', 'remove_move_reconcile')
        group_account_edit = self.env.user.has_group('gard_x_gard.group_account_edit')
        allow_write = action_validate_invoice_payment or action_invoice_open or invoice_refund or move_reconcile or group_account_edit
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
