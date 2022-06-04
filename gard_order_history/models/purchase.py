# -*- coding: utf-8 -*-

# import logging

from odoo import models, fields, api, exceptions, _

# from lxml import etree
# import json

# _logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    invoice_cost_ids = fields.Many2many('account.invoice', string='Cost Invoices',
                                        compute='_get_invoice_cost_ids', copy=False,
                                        readonly=True, track_visibility='onchange')
                                        # store=True, readonly=True, track_visibility='onchange')
    landed_cost_ids = fields.Many2many('stock.landed.cost', string='Landed Costs',
                                       compute='_get_landed_cost_ids', copy=False,
                                       readonly=True, track_visibility='onchange')
                                       # store=True, readonly=True, track_visibility='onchange')

    #  TO DO: search for pickings in group_id of PurchaseOrder
    # @api.depends('order_line.move_ids.returned_move_ids',
    #              'order_line.move_ids.state',
    #              'order_line.move_ids.picking_id')
    # def _compute_picking(self):
    #     res = super(PurchaseOrder, self)._compute_picking()
    #     for order in self:
    #         pickings = self.env['stock.picking']
    #         for line in order.order_line:
    #             # We keep a limited scope on purpose. Ideally, we should also use move_orig_ids and
    #             # do some recursive search, but that could be prohibitive if not done correctly.
    #             group_id_moves = pickings.search([]).filtered(lambda pick: pick.group_id.name == order.name)
    #             pickings |= group_id_moves
    #         order.picking_ids = pickings
    #         # order.picking_count = len(pickings)
    #     return res

    @api.multi
    @api.depends('invoice_ids', 'landed_cost_ids')
    def _get_invoice_cost_ids(self):
        invoice_cost_ids = []
        for order in self:
            if order.invoice_ids:
                invoice_model = self.env['account.invoice']
                invoice_cost_ids = invoice_model.search(
                    [('origin', '=', order.name)]).filtered(lambda ic: ic not in order.invoice_ids)
            order.invoice_cost_ids = invoice_cost_ids

    @api.multi
    @api.depends('picking_ids')
    def _get_landed_cost_ids(self):
        # landed_cost_ids = self.env['stock.landed.cost']
        lc_model = self.env['stock.landed.cost']
        for order in self:
            if order.picking_ids:
                pick_model = self.env['stock.picking']
                picking_ids = order.mapped('picking_ids')
                for pick in picking_ids:
                    landed_cost_ids = lc_model.search(
                        [('picking_ids', 'in', pick.id)])
                    order.landed_cost_ids = landed_cost_ids
