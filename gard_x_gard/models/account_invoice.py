# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

# logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    nit = fields.Char('NIT', size=22, compute="_get_fiscal_data", help="NIT o CI del cliente.")
    razon = fields.Char(u'Razón Social', compute="_get_fiscal_data", help=u"Nombre o Razón Social para la Factura.")

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
        invoice_print = (
            model in "account.invoice" and method in "invoice_print"
        )
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
        # logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        # logger.debug('state >>>>: %s', self.mapped('state'))
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
            # logger.info('Written vals: %s', vals)

    @api.depends("partner_id", "partner_invoice_id")
    def _get_fiscal_data(self):
        if self.partner_id and not self.partner_invoice_id:
            if self.partner_id.commercial_partner_id.nit != 0:
                self.nit = self.partner_id.commercial_partner_id.nit
            elif self.partner_id.commercial_partner_id.ci != 0:
                self.nit = self.partner_id.commercial_partner_id.ci
                self.ci_dept = self.partner_id.commercial_partner_id.ci_dept
            else:
                self.nit = 0

            self.razon = (
                self.partner_id.commercial_partner_id.razon_invoice
                or self.partner_id.commercial_partner_id.razon
                or self.partner_id.commercial_partner_id.name
                or ""
            )
        if self.partner_invoice_id:
            if self.partner_invoice_id.commercial_partner_id.nit != 0:
                self.nit = self.partner_invoice_id.commercial_partner_id.nit
            elif self.partner_invoice_id.commercial_partner_id.ci != 0:
                self.nit = self.partner_invoice_id.commercial_partner_id.ci
                self.ci_dept = self.partner_invoice_id.commercial_partner_id.ci_dept
            else:
                self.nit = 0

            self.razon = (
                self.partner_invoice_id.commercial_partner_id.razon_invoice
                or self.partner_invoice_id.commercial_partner_id.razon
                or self.partner_invoice_id.commercial_partner_id.name
                or ""
            )

    @api.multi
    @api.returns("self")
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        inv_obj = self.env["account.invoice"]
        for invoice in self:
            # create the new invoice
            inv_rel_ref = inv_obj.search(
                [
                    ("partner_id", "=", invoice.partner_id.id),
                    ("reference", "=", invoice.reference),
                ]
            )
            # logger.debug("invoice.reference >>>>: %s", invoice.reference)
            reference = (
                (invoice.reference or "")
                + " "
                + "#"
                + str(len([inv for inv in inv_rel_ref]))
            )
            # logger.debug("reference >>>>: %s", reference)
            invoice["reference"] = reference
        return super().refund(date_invoice, date, description, journal_id)
