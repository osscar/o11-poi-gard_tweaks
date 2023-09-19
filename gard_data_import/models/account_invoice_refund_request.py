# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountInvoiceRefundRequest(models.Model):
    _name = "account.invoice.refund.request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Invoice Refund Request"
    _order = "date_request desc, name desc, id desc"

    def _get_sequence_name(self, vals):
        _logger.debug("_gsn vals init >>>: %s", vals)
        sequence_obj = self.env["ir.sequence"]
        if "company_id" in vals:
            sequence_obj = self.env["ir.sequence"].with_context(
                force_company=vals["company_id"]
            )
        if vals.get("name", _("/")) == _("/"):
            if vals.get("invoice_type") == "out_invoice":
                vals["name"] = sequence_obj.next_by_code(
                    "account.invoice.out.refund.request"
                ) or _("/")
            elif vals.get("invoice_type") == "in_invoice":
                vals["name"] = sequence_obj.next_by_code(
                    "account.invoice.in.refund.request"
                ) or _("/")
        _logger.debug("_gsn vals post >>>: %s", vals)
        return vals

    @api.model
    def create(self, vals):
        vals = self._get_sequence_name(vals)
        return super(AccountInvoiceRefundRequest, self).create(vals)

    name = fields.Char(
        "Order Reference",
        required=True,
        index=True,
        copy=False,
        default=_("/"),
        track_visibility="always",
    )
    company_id = fields.Many2one(
        related="invoice_id.company_id", string="Company", readonly=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("request", "Requested"),
            ("done", "Done"),
            ("except", "Exception"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        # index=True,
        default="draft",
        readonly=True,
        copy=False,
        track_visibility="always",
        help=" * The 'Pending' status is used when a user has created a draft refund invoice to be validated and reconciled.\n"
        " * The 'Done' status is used when the refund invoice has been reconciled with the refunded invoice.\n",
    )
    date_request = fields.Date(
        string="Requested Date",
        readonly=True,
        # states={"draft": [("readonly", False)]},
        default=fields.Date.context_today,
        index=True,
        copy=False,
        track_visibility="onchange",
    )
    date_done = fields.Date(
        string="Date Done",
        readonly=True,
        index=True,
        copy=False,
        track_visibility="onchange",
        help="Keep empty to use the current date.",
    )
    user_id = fields.Many2one(
        "res.users",
        string="Refunded By",
        readonly=True,
        # states={"draft": [("readonly", False)]},
        default=lambda self: self.env.user,
        copy=False,
        track_visibility="onchange",
        help="The user processing this request.",
    )
    request_user_id = fields.Many2one(
        "res.users",
        string="Requested By",
        readonly=True,
        copy=False,
        track_visibility="onchange",
        help="The user processing this request.",
    )
    reason = fields.Selection(
        [
            ("sin", "Fiscal Data"),
            ("date", "Date"),
            ("order", "Order"),
            ("other", "Other"),
        ],
        string="Reason",
        # index=True,
        default=False,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        track_visibility="onchange",
        help=" * Fiscal Data: for Tax ID, name errors.\n"
        " * Date: for date errors.\n"
        " * Order: for order errors (eg. product, quantity, UoM).\n"
        " * Other: for other errors. Please include relevant details in notes.\n",
    )
    description = fields.Char(
        "Reason Notes",
        readonly=True,
        states={"draft": [("readonly", False)]},
        track_visibility="onchange",
    )
    invoice_user_id = fields.Many2one(
        related="invoice_id.user_id",
        readonly=True,
        track_visibility="onchange",
    )
    invoice_id = fields.Many2one(
        "account.invoice",
        "Invoice",
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain=[("state", "in", ("open", "paid"))],
        track_visibility="onchange",
    )
    invoice_type = fields.Selection(
        related="invoice_id.type",
        readonly=True,
        track_visibility="onchange",
    )
    invoice_date = fields.Date(
        related="invoice_id.date_invoice",
        readonly=True,
    )
    invoice_state = fields.Selection(
        related="invoice_id.state",
        readonly=True,
        track_visibility="onchange",
    )
    estado_fac = fields.Selection(
        related="invoice_id.estado_fac",
        readonly=True,
        track_visibility="onchange",
    )
    siat_state = fields.Selection(
        related="invoice_id.siat_state",
        readonly=True,
        track_visibility="onchange",
    )
    refund_invoice_id = fields.Many2one(
        "account.invoice",
        "Refund Invoices",
        # compute="_get_refund_invoice",
        readonly=True,
        track_visibility="onchange",
    )
    refund_invoice_date = fields.Date(
        related="refund_invoice_id.date_invoice",
        readonly=True,
    )
    refund_invoice_state = fields.Selection(
        related="refund_invoice_id.state",
        readonly=True,
        track_visibility="onchange",
    )
    cc_dos = fields.Many2one(
        related="invoice_id.cc_dos",
        track_visibility="onchange",
        readonly=True,
    )
    dos_mode = fields.Selection(
        related="invoice_id.dos_mode",
        track_visibility="onchange",
        readonly=True,
    )
    cuf = fields.Char(
        related="invoice_id.cuf",
        track_visibility="onchange",
        readonly=True,
    )
    order_picking_ids = fields.Many2many(
        "stock.picking",
        compute="_compute_picking",
        # string="Receptions",
        readonly=True,
        store=True,
        track_visibility="onchange",
    )
    stock_move_pending_qty = fields.Float(
        "Qty. Pending",
        compute="_compute_stock_move_pending_qty",
        readonly=True,
        store=True,
        track_visibility="onchange",
    )
    invoice_payment_ids = fields.Many2many(
        related="invoice_id.payment_ids",
        readonly=True,
        track_visibility="onchange",
    )
    invoice_payment_move_line_ids = fields.Many2many(
        related="invoice_id.payment_move_line_ids",
        readonly=True,
        track_visibility="onchange",
    )

    def assign_user_id(self):
        fields_req = ["description", "invoice_id"]
        _logger.debug("_aui getattr fields >>>: %s", (getattr(self, f) for f in fields_req))
        if not any(getattr(self, f) for f in fields_req):
            raise ValidationError(("Please select an invoice and refund reason."))
        self.user_id = self.env.user
        if self.state == "draft":
            if self.name == _("/"):
                vals = {
                    "company_id": self.company_id.id,
                    "invoice_type": self.invoice_type,
                    "name": self.name,
                }
                self.name = self._get_sequence_name(vals)["name"]
            self.state = "request"

    def _check_state(self, state):
        checks = {
            "check_invoice": invoice_id,
            "check_refund_invoice": refund_invoice_id,
            "check_refund": refund_invoice_id in invoice_id.refund_invoice_ids,
        }
        _logger.debug("_cs checks >>>: %s", checks)
        _logger.debug("_cs checks >>>: %s", checks[0])
        if state == "done" and any(checks[0] == False):
            self.state = "exception"

    def _get_picking_ids(self):
        picking_obj = self.env["stock.picking"]
        invoice_id = self.invoice_id

        picking_ids = None
        _logger.debug("_gpi picking_ids >>>: %s", picking_ids)
        _logger.debug("_gpi invoice_id >>>: %s", invoice_id)
        if invoice_id:
            picking_ids = picking_obj.search(
                [("group_id.name", "=", invoice_id.origin)]
            )
            _logger.debug("_gpi if picking_ids >>>: %s", picking_ids)
        _logger.debug("_gpi post picking_ids >>>: %s", picking_ids)
        return picking_ids

    @api.depends(
        "order_picking_ids", "order_picking_ids.move_lines.origin_returned_move_id"
    )
    def _compute_stock_move_pending_qty(self):
        _logger.debug("_csmpq smpq >>>: %s", self.stock_move_pending_qty)
        picking_ids = self.order_picking_ids
        if picking_ids:
            _logger.debug("_csmpq for picking_ids >>>: %s", picking_ids)
            move_lines = [p.move_lines for p in picking_ids]
            if move_lines:
                _logger.debug("_csmpq if move_lines >>>: %s", move_lines)
                
                return_move_lines = [
                    ml.origin_returned_move_id for ml in move_lines
                ]
                qty_pending = sum(0 if ml in return_move_lines else ml.quantity_done for ml in move_lines)
                if return_move_lines:
                    _logger.debug("_csmpq if return_move_lines >>>: %s", return_move_lines)
                    qty_pending = qty_pending - sum(
                        rml.quantity_done for rml in return_move_lines
                    )
                _logger.debug("_csmpq rml_qty_done >>>: %s", qty_pending)
                _logger.debug("_csmpq smpq >>>: %s", self.stock_move_pending_qty)
                self.stock_move_pending_qty = qty_pending
                # self.write({"order_picking_ids": self._get_picking_ids()})
                # return stock_move_pending_qty

    @api.depends("invoice_id", "invoice_state", "estado_fac", "refund_invoice_state")
    def _compute_picking(self):
        if self._get_picking_ids():
            self.order_picking_ids = self._get_picking_ids()
            _logger.debug("_cp picking_ids >>>: %s", self.order_picking_ids)
        if self.state == "done":
            self._check_state(state=self.state)
        # return picking_ids

    # @api.one
    def invoice_payment_unreconcile(self):
        for line in self.invoice_id.payment_move_line_ids:
            line.remove_move_reconcile()
        # return True

    def button_invoice_refund(self):
        _logger.debug("bir _context >>>: %s", self._context)
        # pass invoice as active record for refund wizard
        if self.state != "request":
            raise ValidationError(
                ('Only requests in "Requested" state may be refunded.')
            )
        return {
            "name": "Refund",
            "res_model": "account.invoice.refund",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "context": {
                "active_ids": self.invoice_id.id,
                "active_id": self.invoice_id.id,
                "active_model": self.invoice_id._name,
                "invoice_type": self.invoice_type,
                "description": self.description,
                "invoice_date": self.invoice_id.date_invoice,
            },
            "target": "new",
        }

    # @api.depends("invoice_id", "invoice_state", "estado_fac", "refund_invoice_state")
    # def _get_refund_invoice_id(self):

    # @api.one
    def action_cancel(self):
        if not self.state == "request":
            raise ValidationError(
                ('Only requests in "Requested" state may be cancelled.')
            )
        if not self.refund_invoice_id:
            self.state = "cancel"
