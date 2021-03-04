# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    def write(self, vals):
        move_reconcile = request.params.get('method') in ('assign_outstanding_credit', 'remove_move_reconcile')
        calculate_cash = request.params.get('method') in ('calculate_cash')
        group_account_edit = self.env.user.has_group('gard_x_gard.group_account_edit')
        group_cashier = self.env.user.has_group('gard_x_gard.group_cashier')
        allow_write = move_reconcile or (group_cashier and calculate_cash) or group_account_edit == True
        _logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        _logger.debug('Allow reconcile: %s', move_reconcile)
        _logger.debug('Allow calculate cash: %s', calculate_cash)
        if any(state != 'draft' for state in set(self.mapped('state')) if allow_write == False):
            raise UserError(_('Edit allowed only in draft state. [%s.%s]' % (request.params.get('model'), request.params.get('method'))))
        else:
            _logger.info('Written vals: %s' % vals)
            return super().write(vals)
