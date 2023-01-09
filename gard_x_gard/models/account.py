# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    code = fields.Char(
        string="Short Code",
        size=10,
        required=True,
        help="The journal entries of this journal will be named using this prefix.",
    )
    note = fields.Text("Description")


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def write(self, vals):
        req_model = request.params.get("model")
        req_method = request.params.get("method")
        # account.invoice.refund.invoice_refund
        invoice_refund = (
            req_model == "account.invoice.refund" and req_method == "invoice_refund"
        )
        action_invoice_open = (
            req_model == "account.invoice" and req_method == "action_invoice_open"
        )
        assign_outstanding_credit = (
            req_model == "account.invoice" and req_method == "assign_outstanding_credit"
        )
        action_validate_invoice_payment = (
            req_model == "account.payment" and req_method == "action_validate_invoice_payment"
        )
        immediate_transfer_process = (
            req_method == "immediate.transfer.process"
            # req_model == "stock" and 
        )
        payment_post = (
            req_model == "account.payment" and req_method == "post"
        )
        payment_cancel = (
            req_model == "account.payment" and req_method == "cancel"
        )
        process_reconciliations = (
            req_model == "account.move.line" and req_method == "process_reconciliations"
        )
        action_approve = req_model == ("account.expenses.rendition") and req_method == (
            "action_approve"
        )
        fixable_automatic_asset = self.fixable_automatic_asset
        group_account_edit = self.env.user.has_group("gard_x_gard.group_account_edit")

        allow_write = (
            invoice_refund
            or action_invoice_open
            or action_validate_invoice_payment
            or assign_outstanding_credit
            or immediate_transfer_process
            or payment_post
            or payment_cancel
            or process_reconciliations
            or fixable_automatic_asset
            or action_approve
            or group_account_edit
        )
        if any(
            state != "draft"
            for state in set(self.mapped("state"))
            if allow_write == False
        ):
            raise UserError(
                _(
                    "(%s) Edit allowed only in draft state. [%s.%s]"
                    % (self, request.params.get("req_model"), request.params.get("req_method"))
                )
            )
        else:
            # _logger.info('Written vals: %s' % vals)
            return super().write(vals)
