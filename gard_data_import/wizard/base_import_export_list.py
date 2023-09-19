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

import logging

from odoo import models, fields, api, _, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    # @api.model
    # def _get_reason(self):
    #     res = super()._get_reason()
    #     _logger.debug("_gr self._context >>>: %s", self._context)
    #     reason = self._context.get("description")
    #     if reason:
    #         res = reason
    #     return res

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
            ("sin", "Fiscal Data"),
            ("date", "Date"),
            ("order", "Order"),
            ("other", "Other"),
        ],
        string="Reason",
        default=False,
        required=True,
        copy=False,
        help=" * Fiscal Data: for Tax ID, name errors.\n"
        " * Date: for date errors.\n"
        " * Order: for order errors (eg. product, quantity, UoM).\n"
        " * Other: for other errors. Please include relevant details in notes.\n",
    )

    @api.depends("request_user_id")
    @api.multi
    def _get_invoice_id(self):
        _logger.debug("_gii self._context >>>: %s", self._context)
        # inv_obj = self.env['account.invoice']
        invoices = self.env["account.invoice"].browse(self._context.get("active_id", False))
        if invoices:
            self.invoice_id = invoices
            _logger.debug("_gii self.invoice_id >>>: %s", self.invoice_id)
        else:
            self.invoice_id = []

    @api.multi
    def invoice_refund_request(self):
        req_obj = self.env["account.invoice.refund.request"]

        vals = {
            "invoice_id": self.invoice_id.id,
            "invoice_type": self.invoice_id.type,
            "request_user_id": self.request_user_id.id,
            "reason": self.reason,
            "description": self.description,
            # "state": "request",
        }
        if self.invoice_id.company_id:
            vals["company_id"] = self.invoice_id.company_id.id
            
        request = req_obj.create(vals)
        request["state"] = "request"
        return request
        
    @api.multi
    def compute_refund(self, mode='refund'):
        res = super().compute_refund(mode=mode)
        _logger.debug("_cr res >>>: %s", res)
        