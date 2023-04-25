# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _

from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


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

    @api.model
    def create(self, vals):
        _logger.debug("vals >>>>: %s", vals)
        if "type" in vals:
            partner_ids = []
            if "partner_invoice_id" in vals and vals["type"] in ("out_invoice", "out_refund"):
                partner_ids.append(vals["partner_invoice_id"])
            elif "partner_id" in vals and vals["type"] in ("in_invoice", "in_refund"):
                partner_ids.append(vals["partner_id"])

            if partner_ids:
                partners = self.env["res.partner"].browse(partner_ids)
                for partner in partners:
                    if partner.nit:
                        vals["nit"] = partner.nit
                        vals["ci_dept"] = partner.ci_dept or ""
                    elif partner.ci:
                        vals["nit"] = partner.ci
                        vals["ci_dept"] = partner.ci_dept or ""
                    else:
                        vals["nit"] = 0
                    vals["razon"] = partner.razon_invoice or partner.razon or partner.name or ""

        ret = super(AccountInvoice, self).create(vals)
        return ret

    @api.multi
    @api.returns("self")
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None):
        for invoice in self:
            ref = self._get_ref(invoice)
            if ref:
                invoice.reference = ref
        return super().refund(date_invoice, date, description, journal_id)

    def _get_ref(self, invoice):
        ref = invoice.reference or ""
        inv_rel_ref_ids = self.env["account.invoice"].search([
            ("partner_id", "=", invoice.partner_id.id),
            ("reference", "=", invoice.reference),
            ("id", "!=", invoice.id),
        ])
        count = len(inv_rel_ref_ids)
        if count > 0:
            ref += " #" + str(count)
        return ref


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    _order = "date_invoice desc, id desc"

    state = fields.Selection(
        string="Invoice State", store=True, related="invoice_id.state"
    )
    user_id = fields.Many2one(
        string="Invoice Salesperson", store=True, related="invoice_id.user_id"
    )
    date_invoice = fields.Date(
        string="Invoice Date", store=True, related="invoice_id.date_invoice"
    )
    date_due = fields.Date(
        string="Invoice Date Due", store=True, related="invoice_id.date_due"
    )
    reference = fields.Char(
        string="Invoice Reference", store=True, related="invoice_id.reference"
    )
    invoice_type = fields.Selection(
        related="invoice_id.type", store=True, readonly=True
    )
