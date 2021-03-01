# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def write(self, vals):
        invoice_refund = request.params.get('method') in 'invoice_refund'
        move_reconcile = request.params.get('method') in ('assign_outstanding_credit', 'remove_move_reconcile')
        group_account_edit = self.env.user.has_group('gard_x_gard.group_account_edit')
        _logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        _logger.debug('Allow invoice_refund method: %s', invoice_refund)
        if any(state != 'draft' for state in set(self.mapped('state'))
            if not (group_account_edit or invoice_refund or move_reconcile)):
            raise UserError(_('Edit allowed only in draft state. [%s.%s]' % (request.params.get('model'), request.params.get('method'))))
        else:
            _logger.info('Written vals: %s', vals)
            return super().write(vals)
