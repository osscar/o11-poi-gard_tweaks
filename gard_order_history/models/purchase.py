# -*- coding: utf-8 -*-

# import logging

from odoo import models, fields, api, _

# from lxml import etree
# import json

# _logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    invoice_cost_ids = fields.Many2many(
        comodel_name="account.invoice",
        relation="purchase_order_account_invoice_cost_rel",
        column1="order_id",
        column2="invoice_id",
        string="Cost Invoices",
        compute="_get_invoice_cost_ids",
        copy=False,
        store=True,
        readonly=True,
        track_visibility="onchange",
    )
    landed_cost_ids = fields.Many2many(
        comodel_name="stock.landed.cost",
        relation="purchase_order_stock_landed_cost_rel",
        column1="order_id",
        column2="cost_id",
        string="Landed Costs",
        compute="_get_landed_cost_ids",
        copy=False,
        store=True,
        readonly=True,
        track_visibility="onchange",
    )
    payment_ids = fields.Many2many(
        comodel_name="account.payment",
        relation="purchase_order_account_payment_rel",
        column1="order_id",
        column2="payment_id",
        string="Payments",
        compute="_get_payment_ids",
        copy=False,
        store=True,
        readonly=True,
        track_visibility="onchange",
    )
    account_move_line_ids = fields.Many2many(
        comodel_name="account.move.line",
        relation="purchase_order_account_move_line_rel",
        column1="order_id",
        column2="line_id",
        string="Journal Items",
        compute="_get_account_move_line_ids",
        copy=False,
        store=True,
        readonly=True,
        track_visibility="onchange",
    )
    account_analytic_line_ids = fields.Many2many(
        comodel_name="account.analytic.line",
        relation="purchase_order_account_analytic_line_rel",
        column1="order_id",
        column2="line_id",
        string="Analytic Lines",
        compute="_get_account_analytic_line_ids",
        copy=False,
        store=True,
        readonly=True,
        track_visibility="onchange",
    )

    @api.depends(
        "order_line.move_ids.returned_move_ids",
        "order_line.move_ids.state",
        "order_line.move_ids.picking_id",
    )
    def _compute_picking(self):
        res = super(PurchaseOrder, self)._compute_picking()
        for order in self:
            pickings = self.env["stock.picking"]
            for line in order.order_line:
                for move in line.move_ids:
                    # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
                    # do some recursive search, but that could be prohibitive if not done correctly.
                    moves_group_id = pickings.search(
                        [("group_id", "=", move.picking_id.group_id.id)]
                    )
                    # .filtered(lambda pick: pick.id != line.pick_ids)
                    pickings |= moves_group_id
            order.picking_ids = pickings
            order.picking_count = len(pickings)
        return res

    @api.multi
    @api.depends("account_analytic_id.child_ids", "landed_cost_ids")
    def _get_invoice_cost_ids(self):
        invoice_cost_ids = []
        for order in self:
            if order.account_analytic_id:
                invoice_model = self.env["account.invoice"]
                invoice_cost_ids = invoice_model.search(
                    [
                        (
                            "invoice_line_ids.account_analytic_id.parent_id",
                            "=",
                            order.account_analytic_id.id,
                        )
                    ]
                ).filtered(lambda ic: ic not in order.invoice_ids)
            order.invoice_cost_ids = invoice_cost_ids

    @api.multi
    @api.depends("picking_ids")
    def _get_landed_cost_ids(self):
        lc_model = self.env["stock.landed.cost"]
        for order in self:
            if order.picking_ids:
                picking_ids = order.mapped("picking_ids")
                for pick in picking_ids:
                    landed_cost_ids = lc_model.search([("picking_ids", "in", pick.id)])
                    order.landed_cost_ids = landed_cost_ids

    @api.multi
    @api.depends(
        "invoice_ids.payment_ids",
        "invoice_cost_ids.payment_ids",
    )
    def _get_payment_ids(self):
        for order in self:
            if order.invoice_ids or order.invoice_cost_ids:
                inv_pay = order.mapped("invoice_ids").mapped("payment_ids")
                invc_pay = order.mapped("invoice_cost_ids").mapped("payment_ids")
                pay_ids = inv_pay + invc_pay
                order.payment_ids = pay_ids

    @api.multi
    @api.depends(
        "invoice_ids",
        "invoice_cost_ids",
        "payment_ids",
        "picking_ids",
        "landed_cost_ids",
    )
    def _get_account_move_line_ids(self):
        for order in self:
            # Get the move line IDs from the invoice(s)
            invoice_move_line_ids = order.invoice_ids.mapped("move_id.line_ids")
            invoice_cost_move_line_ids = order.invoice_cost_ids.mapped(
                "move_id.line_ids"
            )

            # Get the move line IDs from the invoice payments
            payment_move_line_ids = order.payment_ids.mapped("move_line_ids")

            # Get the move line IDs from the stock pickings
            picking_move_line_ids = order.picking_ids.mapped("move_id.line_ids")

            # Get a list of all move line IDs from invoices, invoice payments, and stock pickings
            all_move_line_ids = [move_line.id for move_line in invoice_move_line_ids]
            all_move_line_ids.extend(
                move_line.id for move_line in invoice_cost_move_line_ids
            )
            all_move_line_ids.extend(
                move_line.id for move_line in payment_move_line_ids
            )
            all_move_line_ids.extend(
                move_line.id for move_line in picking_move_line_ids
            )

            # Remove duplicates and convert the result to a list
            unique_move_line_ids = list(set(all_move_line_ids))

            # Return the unique move line IDs as a list
            order.account_move_line_ids = unique_move_line_ids

    @api.multi
    @api.depends(
        "account_move_line_ids",
        "account_analytic_id.child_ids.line_ids",
    )
    def _get_account_analytic_line_ids(self):
        for order in self:
            # Get the move line IDs from the invoice payments
            analytic_line_ids = order.account_analytic_id.child_ids.mapped("line_ids")

            all_analytic_line_ids = [line.id for line in analytic_line_ids]
            # Remove duplicates and convert the result to a list
            unique_analytic_line_ids = list(set(all_analytic_line_ids))

            # Return the unique move line IDs as a list
            order.account_analytic_line_ids = unique_analytic_line_ids

    @api.multi
    def action_view_account_move_lines(self):
        action = self.env.ref('account.action_account_moves_all_a')
        result = action.read()[0]
        
        #override the context to get rid of the default filtering
        result['context'] = {}
        aml_ids = self.mapped('account_move_line_ids')
        result['domain'] = "[('id','in',%s)]" % (aml_ids.ids)
        return result
    
    @api.multi
    def action_view_account_analytic_lines(self):
        action = self.env.ref('analytic.account_analytic_line_action_entries')
        result = action.read()[0]
        
        #override the context to get rid of the default filtering
        result['context'] = {}
        aal_ids = self.mapped('account_analytic_line_ids')
        result['domain'] = "[('id','in',%s)]" % (aal_ids.ids)
        return result