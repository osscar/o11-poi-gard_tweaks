# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    # _rec_name = "record_name"

    # record_name = fields.Char('Complete Name', compute='_compute_record_name', store=True)
    refund_request_ids = fields.One2many(
        comodel_name="account.invoice.refund.request",
        inverse_name="invoice_id",
        readonly=True,
    )
    refund_request_info = fields.Char(
        string="Requests", compute="_compute_refund_request_ids"
    )

    @api.depends("refund_request_ids")
    def _compute_refund_request_ids(self):
        for invoice in self:
            request_count = len(invoice.refund_request_ids)
            request_state = False
            if invoice.refund_request_ids:
                request_state = (
                    "Pending"
                    if any(rq.state != "done" for rq in invoice.refund_request_ids)
                    else "Done"
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

    # @api.depends('number', 'origin', "cc_nro")
    # def _compute_record_name(self):
    #     if self:
    #         for invoice in self:
    #             _logger.debug("_crn self >>>: %s", invoice)
    #             ref = invoice.cc_nro or invoice.supplier_invoice_number or invoice.reference
    #             origin = invoice.origin

    #             record_name = invoice.number
    #             _logger.debug("_crn ref >>>: %s", ref)
    #             _logger.debug("_crn origin >>>: %s", origin)
    #             _logger.debug("_crn rn >>>: %s", record_name)
    #             if ref:
    #                 record_name = '%s: F%s' % (record_name, ref)
    #                 _logger.debug("_crn if ref rn >>>: %s", record_name)
    #             if origin:
    #                 record_name = '%s / %s' % (record_name, origin)
    #                 _logger.debug("_crn if origin rn >>>: %s", record_name)

    #             invoice.record_name = record_name
    #             _logger.debug("_crn if ref rn >>>: %s", record_name)
