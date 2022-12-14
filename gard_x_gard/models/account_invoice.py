# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

from odoo.exceptions import UserError
from odoo.http import request

# _logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    nit = fields.Char(
        "NIT",
        size=22,
        help="NIT o CI del cliente.",
    )
    razon = fields.Char(
        "Razón Social",
        help="Nombre o Razón Social para la Factura.",
    )

    @api.multi
    def write(self, vals):
        model = request.params.get("model")
        method = request.params.get("method")
        action_invoice_open = method in "action_invoice_open"
        action_validate_invoice_payment = method in "action_validate_invoice_payment"
        invoice_refund = method in "invoice_refund"
        move_reconcile = method in (
            "assign_outstanding_credit",
            "remove_move_reconcile",
        )
        payment_post = model in "account.payment" and method in "post"
        send_mail_action = (
            model in "mail.compose.message" and method in "send_mail_action"
        )
        siat_recepcionFactura = (
            model in "account.invoice" and method in "siat_recepcionFactura"
        )
        siat_recepcionPaqueteFactura = (
            model in "account.invoice" and method in "siat_recepcionPaqueteFactura"
        )
        invoice_print = model in "account.invoice" and method in "invoice_print"
        group_account_edit = self.env.user.has_group("gard_x_gard.group_account_edit")
        allow_write = (
            action_validate_invoice_payment
            or action_invoice_open
            or invoice_refund
            or move_reconcile
            or payment_post
            or group_account_edit
            or send_mail_action
            or siat_recepcionFactura
            or siat_recepcionPaqueteFactura
            or invoice_print
        )
        # _logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        # _logger.debug('state >>>>: %s', self.mapped('state'))
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
            return super().write(vals)
            # _logger.info('Written vals: %s', vals)

    @api.model
    def create(self, vals):
        # _logger.debug('vals >>>>: %s', vals)
        if 'partner_invoice_id' in vals:
            # _logger.debug('vals[pinvid] >>>>: %s', vals['partner_invoice_id'])
            partner_invoice_id = self.env['res.partner'].browse(vals['partner_invoice_id'])
            if partner_invoice_id.nit != 0:
                vals['nit'] = partner_invoice_id.nit
            elif partner_invoice_id.ci != 0:
                vals['nit'] = partner_invoice_id.ci
                vals['ci_dept'] = partner_invoice_id.ci_dept
            else:
                vals['nit'] = 0

            vals['razon'] = (
                partner_invoice_id.razon_invoice
                or partner_invoice_id.razon
                or partner_invoice_id.name
                or ""
            )
            # _logger.debug('vals_pinvid >>>>: %s', vals)

        ret = super(AccountInvoice, self).create(vals)
        return ret    

    @api.multi
    @api.returns("self")
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        inv_obj = self.env["account.invoice"]
        for invoice in self:
            # create the new invoice
            inv_rel_ref_ids = inv_obj.search(
                [
                    ("partner_id", "=", invoice.partner_id.id),
                    ("reference", "=", invoice.reference),
                ]
            )
            # _logger.debug("invoice.reference >>>>: %s", invoice.reference)
            if inv_rel_ref_ids:
                reference = (
                    invoice.reference or ""
                    + " "
                    + "#"
                    + str(len([inv for inv in inv_rel_ref_ids]))
                )
                # _logger.debug("reference >>>>: %s", reference)
                invoice["reference"] = reference
        return super().refund(date_invoice, date, description, journal_id)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    _order = "date_invoice desc, id desc"

    @api.multi
    def write(self, vals):
        model = request.params.get("model")
        method = request.params.get("method")
        action_invoice_open = method in "action_invoice_open"
        action_validate_invoice_payment = method in "action_validate_invoice_payment"
        invoice_refund = method in "invoice_refund"
        move_reconcile = method in (
            "assign_outstanding_credit",
            "remove_move_reconcile",
        )
        payment_post = model in "account.payment" and method in "post"
        send_mail_action = (
            model in "mail.compose.message" and method in "send_mail_action"
        )
        siat_recepcionFactura = (
            model in "account.invoice" and method in "siat_recepcionFactura"
        )
        invoice_print = model in "account.invoice" and method in "invoice_print"
        group_account_edit = self.env.user.has_group("gard_x_gard.group_account_edit")
        allow_write = (
            action_validate_invoice_payment
            or action_invoice_open
            or invoice_refund
            or move_reconcile
            or payment_post
            or group_account_edit
            or send_mail_action
            or siat_recepcionFactura
            or invoice_print
        )
        # _logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        # _logger.debug('state >>>>: %s', self.mapped('state'))
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
            return super().write(vals)
            # _logger.info('Written vals: %s', vals)

    state = fields.Selection(string="Invoice State", store=True, related="invoice_id.state")
    user_id = fields.Many2one(string='Invoice Salesperson', store=True, related="invoice_id.user_id")
    date_invoice = fields.Date(string='Invoice Date', store=True, related="invoice_id.date_invoice")
    date_due = fields.Date(string='Invoice Date Due', store=True, related="invoice_id.date_due")
    reference = fields.Char(string='Invoice Reference', store=True, related="invoice_id.reference")
    invoice_type = fields.Selection(related='invoice_id.type', store=True, readonly=True)