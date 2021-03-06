# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AccountDeposit(models.Model):
    _inherit = 'account.deposit'

    payment_ids = fields.Many2many("account.payment", string='Payments', compute="_get_payments", readonly=True, copy=False)
    payment_count = fields.Integer(string='# of Payments', compute='_get_payments', readonly=True)

    @api.multi
    def action_view_payments(self):
        action = self.env.ref('account.action_account_payments').read()[0]
        _logger.debug('Payments >>>>: %s', self.payment_ids)
        _logger.debug('Payment Count >>>>: %s', len(set(self.payment_ids.ids)))
        if self.payment_count > 1:
            action['domain'] = [('id', 'in', self.payment_ids.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _get_payments(self):
        for deposit in self:
            payment_ids = self.env['account.payment'].search([('deposit_id', '=', deposit.id)])
            deposit.update({
                'payment_ids': payment_ids.ids,
                'payment_count': len(set(payment_ids.ids)),
            })
