#!/usr/bin/env python
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Poiesis Consulting (<http://www.poiesisconsulting.com>).
#    Autor: Nicolas Bustillos
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from dateutil.relativedelta import relativedelta
from datetime import datetime

import logging

from odoo import models, fields, api, _, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    @api.model
    def _get_reason(self):
        res = super()._get_reason()
        _logger.debug("_gr self._context >>>: %s", self._context)
        reason = self._context.get("reason")
        _logger.debug("_gr reason >>>: %s", reason)
        if reason:
            res = reason
        return res

    request_user_id = fields.Many2one(
        "res.users",
        string="Refunded By",
        readonly=True,
        default=lambda self: self.env.user,
        copy=False,
        help="The user processing this request.",
    )
    invoice_id = fields.Many2one(
        "account.invoice",
        "Invoice",
        compute="_get_invoice_id",
    )
    invoice_user_id = fields.Many2one(
        related="invoice_id.user_id",
        readonly=True,
    )
    invoice_date = fields.Date(
        related="invoice_id.date_invoice",
        readonly=True,
    )
    reason = fields.Selection(
        [
            ("fiscal", "Fiscal Data"),
            ("order", "Order"),
            ("other", "Other"),
        ],
        string="Reason",
        # required=True,
        copy=False,
        help=" * Fiscal Data: for Tax ID, name errors.\n"
        " * Order: for order errors (eg. product, quantity, UoM).\n"
        " * Other: for other errors. Please include relevant details in notes.\n",
    )
    date_range = fields.Selection(
        [
            ("request", "In Range"),
            ("except", "Out of Range"),
        ],
        string="Date Range",
        readonly=True,
        copy=False,
        help=" * Date Range for request.\n"
        " * In Range: Refund request within refund date range.\n"
        " * Out of Range: Refund request out of refund date range. Requires non-normal procedures.\n",
    )

    @api.depends("request_user_id")
    @api.multi
    def _get_invoice_id(self):
        invoices = self.env["account.invoice"].browse(
            self._context.get("active_id", False)
        )
        if invoices:
            self.invoice_id = invoices
            self.date_range = self._date_range(self.invoice_id.date_invoice)
            self.onchange_invoice_id()

    @api.onchange("invoice_id")
    def onchange_invoice_id(self):
        self.filter_refund = self._context.get("filter_refund", "cancel") 
        self.date_invoice = self._context.get("invoice_date", self.invoice_id.date_invoice)
        self.date = self._context.get("invoice_date", self.invoice_id.date_invoice)
        self.reason = self._context.get("reason")
        self.description = self._context.get("description") or self.reason

    def _date_range(self, date):
        date_range = "request"
        if self.invoice_id.type == "out_invoice":
            date_range = "except"    
            today = fields.Date.from_string(fields.Date.context_today(self))
            date = fields.Date.from_string(date)
            range_domain = False
            if date:
                range_curr_month = [date <= (today + relativedelta(day=31)), date >= (today - relativedelta(day=1))]
                # range_prev_month = [date >= (today - relativedelta(months=1)), ]
                range_domain = range_curr_month
            if all(range_domain):
                date_range = "request"
        return date_range
            
    def invoice_refund_request(self):
        req_obj = self.env["account.invoice.refund.request"]
        vals = {
            "invoice_id": self.invoice_id.id,
            "invoice_type": self.invoice_id.type,
            "request_user_id": self.request_user_id.id,
            "reason": self.reason,
            "description": self.description,
        }
        if self.invoice_id.company_id:
            vals["company_id"] = self.invoice_id.company_id.id
        request = req_obj.with_context(assign_user="True").create(vals)
        request["state"] = self.date_range
        return request

    def compute_refund(self, mode="refund"):
        res = super().compute_refund(mode=mode)
        # env objects
        inv_obj = self.env["account.invoice"]
        req_obj = self.env["account.invoice.refund.request"]
        # get data
        ref_inv = inv_obj.search(res["domain"])
        request_id = self._context.get("request_id")
        req_rf_inv = req_obj.search([("id", "=", request_id)], limit=1)
        # write refund invoice to refund request
        if req_rf_inv:
            req_rf_inv["refund_invoice_id"] = ref_inv
        return res
