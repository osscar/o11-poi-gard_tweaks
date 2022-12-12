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
        model = request.params.get("model")
        method = request.params.get("method")
        # account.invoice.refund.invoice_refund
        invoice_refund = (
            model in "account.invoice.refund" and method in "invoice_refund"
        )
        action_invoice_open = (
            model in "account.invoice" and method in "action_invoice_open"
        )
        action_validate_invoice_payment = (
            model in "account.payment" and method in "action_validate_invoice_payment"
        )
        fixable_automatic_asset = self.fixable_automatic_asset
        group_account_edit = self.env.user.has_group("gard_x_gard.group_account_edit")

        allow_write = (
            invoice_refund
            or action_invoice_open
            or action_validate_invoice_payment
            or fixable_automatic_asset
            or group_account_edit
        )
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
            # _logger.info('Written vals: %s' % vals)
            return super().write(vals)
