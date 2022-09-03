# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    # account_payment.write method customization to implement write restrictions
    @api.multi
    def write(self, vals):
        process_reconciliations = request.params.get("method") in (
            "process_reconciliations"
        )
        move_reconcile = request.params.get("method") in (
            "assign_outstanding_credit",
            "remove_move_reconcile",
        )
        # account.deposit allowed methods
        calculate_cash = request.params.get("model") in (
            "account.deposit"
        ) and request.params.get("method") in ("calculate_cash")
        action_reset = request.params.get("model") in (
            "account.deposit"
        ) and request.params.get("method") in ("action_reset")
        cancel_cash = request.params.get("model") in (
            "account.deposit"
        ) and request.params.get("method") in ("cancel_cash")
        cancel = request.params.get("method") in ("cancel")
        action_draft = request.params.get("method") in ("action_draft")
        acc_pay_req_write = request.params.get("model") in (
            "account.payment.request"
        ) and request.params.get("method") in ("write")
        # post = request.params.get('method') in ('post')
        group_cashier = self.env.user.has_group("gard_x_gard.group_cashier")
        group_account_edit = self.env.user.has_group("gard_x_gard.group_account_edit")
        allow_write = (
            move_reconcile
            or (group_cashier and (calculate_cash or action_reset or cancel_cash))
            or cancel
            or action_draft
            or process_reconciliations
            or group_account_edit
            or acc_pay_req_write
        )
        # _logger.debug('acc_pay write Requested params method >>>: [%s.%s]' % (
        # request.params.get('model'), request.params.get('method')))
        if any(
            state != "draft"
            for state in set(self.mapped("state"))
            if allow_write == False
        ):
            raise UserError(
                _(
                    "Edit allowed only in draft state. [%s.%s]"
                    % (request.params.get("model"), request.params.get("method"))
                )
            )
        else:
            _logger.info("Written vals: %s" % vals)
            return super().write(vals)
