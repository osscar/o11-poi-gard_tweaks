# -*- coding: utf-8 -*-
import logging, copy

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
        # compute="_check_state",
        # store=True,
        # index=True,
        default="draft",
        readonly=True,
        copy=False,
        track_visibility="always",
        help=" * 'Draft': refund request is created but not yet requested.\n"
        " * 'Requested': refund request has been requested.\n"
        " * 'Done': refund has been processed succesfully.\n"
        " * 'Except': refund request has exceptions.\n"
        " * 'Cancel': refund request has been cancelled.\n",
    )
    date_request = fields.Date(
        string="Request Date",
        readonly=True,
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
        string="Assigned User",
        readonly=True,
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
            ("fiscal", "Fiscal Data"),
            ("order", "Order"),
            ("other", "Other"),
        ],
        string="Reason",
        default=False,
        required=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        track_visibility="onchange",
        help=" * Fiscal Data: for Tax ID, name errors.\n"
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
        required=True,
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
    invoice_sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        relation="refund_request_sale_order_ids_rel",
        compute="_compute_invoice_order_ids",
        readonly=True,
        store=True,
        track_visibility="onchange",
    )
    invoice_purchase_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        relation="refund_request_purchase_order_ids_rel",
        compute="_compute_invoice_order_ids",
        readonly=True,
        store=True,
        track_visibility="onchange",
    )
    invoice_date = fields.Date(
        related="invoice_id.date_invoice",
        readonly=True,
    )
    invoice_state = fields.Selection(
        related="invoice_id.state",
        string="Invoice State",
        readonly=True,
        track_visibility="onchange",
    )
    invoice_state_display = fields.Selection(
        related="invoice_state",
        readonly=True,
    )
    estado_fac = fields.Selection(
        related="invoice_id.estado_fac",
        readonly=True,
        track_visibility="onchange",
    )
    estado_fac_display = fields.Selection(
        related="estado_fac",
        readonly=True,
    )
    siat_state = fields.Selection(
        related="invoice_id.siat_state",
        readonly=True,
        track_visibility="onchange",
    )
    siat_state_display = fields.Selection(
        related="siat_state",
        readonly=True,
    )
    refund_invoice_id = fields.Many2one(
        "account.invoice",
        "Refund Invoice",
        readonly=True,
        track_visibility="onchange",
    )
    refund_invoice_date = fields.Date(
        related="refund_invoice_id.date_invoice",
        string="Refund Invoice Date",
        readonly=True,
    )
    refund_invoice_state = fields.Selection(
        related="refund_invoice_id.state",
        string="Refund Invoice State",
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
    invoice_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        relation="refund_request_picking_ids_rel",
        compute="_compute_invoice_picking_ids",
        readonly=True,
        store=True,
        track_visibility="onchange",
    )
    invoice_stock_move_ids = fields.Many2many(
        comodel_name="stock.move",
        compute="_compute_invoice_stock_move_ids",
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
    stock_move_pending_qty_display = fields.Float(
        related="stock_move_pending_qty",
        readonly=True,
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

    @api.multi
    def _write(self, vals):
        for request in self:
            user = request.user_id
            if user and self._context.get("active_test") != False:
                if user != self.env.user and not request._context.get("assign_user"):
                    raise ValidationError(
                        ("Please reassign the request to yourself to continue.")
                    )
            if "invoice_stock_move_ids" in vals:
                vals["state"] = request._check_state()
        return super()._write(vals)

    def button_assign_user_id(self):
        fields_req = ["description", "invoice_id"]
        if not any(getattr(self, f) for f in fields_req):
            raise ValidationError(("Please select an invoice and refund reason."))
        ctx = self.with_context(assign_user="True")
        ctx.user_id = self.env.user
        if self.state == "draft":
            if self.name == _("/"):
                vals = {
                    "company_id": self.company_id.id,
                    "invoice_type": self.invoice_type,
                    "name": self.name,
                }
                ctx.name = self._get_sequence_name(vals)["name"]
            ctx.state = "request"

    @api.multi
    def _check_state(self):
        invoice_state = self.invoice_state
        refund_invoice_state = self.refund_invoice_state
        state = self.state
        check_done = {
            "check_invoice_state": invoice_state == "paid",
            "check_refund_invoice_state": refund_invoice_state == "paid",
            "check_estado_fac": self.estado_fac == "A",
            "check_siat_state": self.siat_state == "anulada",
            "check_pickings_state": all(
                p.state in ("done", "cancel") for p in self.invoice_picking_ids
            ),
            "check_qty_pending": self.stock_move_pending_qty == 0,
        }
        if state == "done":
            if not all(check_done.values()):
                state = "except"
        elif state in ("request", "except"):
            if all(check_done.values()):
                state = "done"
        return state

    @api.multi
    @api.depends(
        "user_id",
        "invoice_id",
    )
    def _compute_invoice_order_ids(self):
        for request in self:
            order_ids = []
            order_type = False
            if request.invoice_id:
                invoice_type = request.invoice_type
                if invoice_type == "out_invoice":
                    order_type = "sale"
                elif invoice_type == "in_invoice":
                    order_type = "purchase"
                get_order_ids = []
                if request.invoice_id.invoice_line_ids:
                    for inv_line in request.invoice_id.invoice_line_ids:
                        il_order_line_ids = str(order_type + "_line_ids")
                        get_order_ids = [
                            o["id"]
                            for ol in inv_line[il_order_line_ids]
                            for o in ol["order_id"]
                        ]
                order_ids = self.env[str(order_type + ".order")]
                order_ids = order_ids.search([("id", "in", get_order_ids)])
            if order_type:
                order_field = str("invoice_" + order_type + "_order_ids")
                request[order_field] = order_ids

    @api.multi
    @api.depends(
        "invoice_sale_order_ids.picking_ids",
        "invoice_purchase_order_ids.picking_ids",
    )
    def _compute_invoice_picking_ids(self):
        for request in self:
            pick_ids = self.env["stock.picking"]
            get_pick_ids = []
            if request.invoice_sale_order_ids or request.invoice_purchase_order_ids:
                if self.invoice_type == "out_invoice":
                    get_pick_ids = [
                        p.id
                        for so in request.invoice_sale_order_ids
                        for p in so.picking_ids
                    ]
                elif self.invoice_type == "in_invoice":
                    get_pick_ids = [
                        p.id
                        for po in request.invoice_purchase_order_ids
                        for p in so.picking_ids
                    ]
            pick_ids = pick_ids.search([("id", "in", get_pick_ids)])
            request.invoice_picking_ids = pick_ids

    @api.multi
    @api.depends(
        "invoice_picking_ids.state",
        "invoice_state",
        "refund_invoice_state",
    )
    def _compute_invoice_stock_move_ids(self):
        for request in self:
            sm_ids = [sm.id for p in request.invoice_picking_ids for sm in p.move_lines]
            request.invoice_stock_move_ids = sm_ids

    @api.depends(
        "invoice_stock_move_ids.state",
    )
    @api.multi
    def _compute_stock_move_pending_qty(self):
        qty_pending = 0.0
        for move in self:
            if move.invoice_stock_move_ids:
                smoves = move.invoice_stock_move_ids
                rmoves = smoves.mapped("returned_move_ids")
                if rmoves:
                    smoves = smoves.filtered(lambda s: s not in rmoves)
                qty_pending_smoves = sum(sm.quantity_done for sm in smoves)
                qty_pending_rmoves = sum(rm.quantity_done for rm in rmoves)
                qty_pending = qty_pending_smoves - qty_pending_rmoves
            move.stock_move_pending_qty = qty_pending

    def button_invoice_payment_unreconcile(self):
        for line in self.invoice_id.payment_move_line_ids:
            line.remove_move_reconcile()

    def button_invoice_siat_cancel(self):
        # pass invoice as active record for refund wizard
        if self.user_id != self.env.user:
            raise ValidationError(
                ("Please reassign the request to yourself to continue.")
            )
        if (
            self.state != "request"
            or self.stock_move_pending_qty != 0
            or any(
                sm.state not in ("done", "cancel") for sm in self.invoice_stock_move_ids
            )
        ):
            raise ValidationError(
                (
                    "Request is not ready for this action. Check that stock moves "
                    "have been returned and try again."
                )
            )
        return self.invoice_id.action_wizard_anulacion()

    def button_invoice_refund(self):
        # pass invoice as active record for refund wizard
        if self.state != "request":
            raise ValidationError(
                ('Only requests in "Requested" state may be refunded.')
            )
        if (
            any(p.state not in ("done", "cancel") for p in self.invoice_picking_ids)
        ) or self.stock_move_pending_qty != 0:
            raise ValidationError(
                (
                    "Pickings must be cancelled or done, and pending quantity must be 0 before refunding the invoice."
                )
            )
        if self.refund_invoice_id:
            raise ValidationError(
                ("The invoice already has a refund registered in this request.")
            )
        if self.siat_state != "anulada":
            raise ValidationError(
                ("SIAT state must be 'anulada' before refunding the invoice.")
            )
        return {
            "name": "Refund",
            "res_model": "account.invoice.refund",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            # "view_id": self.env.ref("gard_account_invoice_refund.view_account_invoice_refund_request").id,
            "context": {
                "active_ids": self.invoice_id.id,
                "active_id": self.invoice_id.id,
                "active_model": self.invoice_id._name,
                "invoice_id": self.invoice_id.id,
                "invoice_type": self.invoice_type,
                "filter_refund": "cancel",
                "description": self.description,
                "reason": self.reason,
                "invoice_date": self.invoice_date,
                "request_id": self.id,
            },
            "target": "new",
        }

    def action_cancel(self):
        if not self.state == "request":
            raise ValidationError(
                ('Only requests in "Requested" state may be cancelled.')
            )
        if not self.refund_invoice_id:
            self.state = "cancel"
