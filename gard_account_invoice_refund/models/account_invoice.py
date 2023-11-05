# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    refund_request_ids = fields.One2many(
        comodel_name="account.invoice.refund.request",
        inverse_name="invoice_id",
        readonly=True,
    )
    refund_request_info = fields.Char(
        string="Requests", compute="_compute_refund_request_ids"
    )

    @api.multi
    def name_get(self):
        res = []
        for invoice in self:
            ref = str(invoice.cc_nro or invoice.supplier_invoice_number or invoice.reference)
            origin = invoice.origin
            record_name = invoice.number or ""
            if ref:
                record_name = ": ".join([record_name, ref])
            if origin:
                record_name = " / ".join([record_name, origin])
            res.append((invoice.id, record_name))
        return res

    @api.depends("refund_request_ids")
    def _compute_refund_request_ids(self):
        for invoice in self:
            _logger.debug(
                "_crri invoice.refund_request_ids >>>: %s", invoice.refund_request_ids
            )
            request_count = len(invoice.refund_request_ids)
            request_state = False
            if invoice.refund_request_ids:
                request_state = (
                    _("Pending")
                    if any(rq.state != "done" for rq in invoice.refund_request_ids)
                    else _("Done")
                )
            invoice.refund_request_info = (
                str(request_count) + ": " + (request_state or "")
            )

    @api.multi
    def action_view_refund_request(self):
        """
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        """
        action = self.env.ref(
            "gard_account_invoice_refund.action_account_invoice_refund_request"
        ).read()[0]

        requests = self.mapped("refund_request_ids")
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (
                    self.env.ref(
                        "gard_account_invoice_refund.view_account_invoice_refund_request_form"
                    ).id,
                    "form",
                )
            ]
            action["res_id"] = requests.id
        return action
