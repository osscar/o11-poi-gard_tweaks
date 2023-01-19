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
        req_model = request.params.get("model")
        req_method = request.params.get("method")

        process_reconciliations = req_method in (
            "process_reconciliations"
        )
        move_reconcile = req_method in (
            "assign_outstanding_credit",
            "remove_move_reconcile",
        )
        # account.deposit allowed methods
        calculate_cash = req_model in (
            "account.deposit"
        ) and req_method in ("calculate_cash")
        action_reset = req_model in (
            "account.deposit"
        ) and req_method in ("action_reset")
        cancel_cash = req_model in (
            "account.deposit"
        ) and req_method in ("cancel_cash")
        cancel = req_method in ("cancel")
        action_draft = req_method in ("action_draft")
        acc_pay_req_write = req_model in (
            "account.payment.request"
        ) and req_method in ("write")
        rend_action_cancel = req_model in (
            "account.expenses.rendition"
        ) and req_method in ("action_cancel")
        # post = request.params.get('method') in ('post')
        group_cashier = self.env.user.has_group("gard_x_gard.group_cashier")
        group_account_edit = self.env.user.has_group("gard_x_gard.group_account_edit")
        allow_write = (
            process_reconciliations
            or move_reconcile
            or (group_cashier and (calculate_cash or action_reset or cancel_cash))
            or cancel
            or action_draft
            or acc_pay_req_write
            or rend_action_cancel
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
                    "(%s) Edit allowed only in draft state. [%s.%s]"
                    % (self, req_model, req_method)
                )
            )
        else:
            _logger.info("Written vals: %s" % vals)
            return super().write(vals)
