# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, exceptions, _

# from lxml import etree
# import json

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    landed_cost_ids = fields.Many2many('stock.landed.cost', string='Landed Costs',
                                       compute='_get_landed_cost_ids', copy=False, readonly=True, track_visibility='onchange')
    invoice_cost_ids = fields.Many2many('account.invoice', string='Cost Invoices',
                                       compute='_get_invoice_cost_ids', copy=False, readonly=True, track_visibility='onchange')
    invoice_am_ids = fields.Many2many('account.move', string='Purchase Invoices Journal Entries',
                                      compute='_get_account_move_ids', copy=False, readonly=True, track_visibility='onchange')
    invoice_cost_am_ids = fields.Many2many('account.move', string='Cost Invoices Journal Entries',
                                      compute='_get_account_move_ids', readonly=True, track_visibility='onchange')
    picking_am_ids = fields.Many2many('account.move', string='Pickings Journal Entries',
                                      compute='_get_account_move_ids', copy=False, readonly=True, track_visibility='onchange')
    landed_cost_am_ids = fields.Many2many('account.move', string='Landed Costs Journal Entries',
                                          compute='_get_account_move_ids', copy=False, readonly=True, track_visibility='onchange')
    balance_inv_am = fields.Float(string='PInvoices  =',
                                     compute='_compute_account_results')
    balance_pick_am = fields.Float(string='Picks  =',
                                     compute='_compute_account_results')
    balance_invc_am = fields.Float(string='CInvoices  =',
                                     compute='_compute_account_results')
    balance_lcost_am = fields.Float(string='LCosts  =',
                                     compute='_compute_account_results')
    balance_inv_stock_cost = fields.Float(string='PInvs - Picks  =',
                                     compute='_compute_account_results')
    balance_invc_lcost = fields.Float(string='CInvs - LCosts  =',
                                     compute='_compute_account_results')

    @api.multi
    @api.depends('picking_ids')
    def _get_landed_cost_ids(self):
        landed_cost_ids = []
        for order in self:
            if order.picking_ids:
                slc_model = self.env['stock.landed.cost']
                picking_ids = order.mapped('picking_ids')
                # _logger.debug('>>>>: %s', (order.invoice_payment_ids))
                for lc in landed_cost_ids:
                    landed_cost_ids = slc_model.search(
                        [('picking_ids', 'in', picking_ids.id)])
                # _logger.debug('>>>>: %s', (landed_cost_ids))
        order.landed_cost_ids = landed_cost_ids

    @api.multi
    @api.depends('invoice_ids')
    def _get_invoice_cost_ids(self):
        invoice_cost_ids = []
        for order in self:
            if order.invoice_ids:
                invoice_model = self.env['account.invoice']
                # _logger.debug('>>>>: %s', (order.invoice_payment_ids))
                invoice_cost_ids = invoice_model.search(
                    [('origin', '=', order.name)])
                # _logger.debug('>>>>: %s', (landed_cost_ids))
        order.invoice_cost_ids = invoice_cost_ids.filtered(lambda ic: ic not in self.invoice_ids)

    @api.multi
    @api.depends('invoice_ids', 'picking_ids', 'landed_cost_ids')
    def _get_account_move_ids(self):
        model_aml = self.env['account.move.line']
        invoice_am_ids = []
        picking_am_ids = []
        landed_cost_am_ids = []
        for order in self:
            if order.invoice_ids:
                invoice_am_ids = order.mapped('invoice_ids').mapped(
                    'move_id')
                invoice_cost_am_ids = order.mapped('invoice_cost_ids').mapped(
                    'move_id')
                order.invoice_am_ids = invoice_am_ids
                # _logger.debug('>>>>: %s', (invoice_cost_am_ids.filtered(lambda icam: icam.id != set(invoice_am_ids))))
                # order.invoice_cost_am_ids = invoice_cost_am_ids.filtered(lambda icam: icam.id != set(invoice_am_ids))
                order.invoice_cost_am_ids = invoice_cost_am_ids
            if order.picking_ids:
                picking_ids = order.mapped('picking_ids')
                pick_sm_ids = picking_ids.mapped('move_lines')
                for pick in picking_ids:
                    picking_aml_ids = model_aml.search(
                        [('ref', '=', pick.name)])
                    for aml in picking_aml_ids:
                        picking_am_ids=aml.mapped('move_id')
                order.picking_am_ids = picking_am_ids
            if order.landed_cost_ids:
                landed_cost_ids=order.mapped('landed_cost_ids')
                landed_cost_am_ids=landed_cost_ids.mapped('account_move_id')
                order.landed_cost_am_ids = landed_cost_am_ids

    @ api.depends('invoice_am_ids', 'picking_am_ids', 'landed_cost_am_ids')
    def _compute_account_results(self):
        balance_cost_inv_landed_cost = 0
        sum_inv_am = 0
        sum_pick_am = 0
        sum_invc_am = 0
        sum_lc_am = 0
        if self.invoice_ids and self.picking_ids:
            for inv_am in self.invoice_am_ids:
                sum_inv_am += inv_am.amount
                self.balance_inv_am = sum_inv_am
            for pick_am in self.picking_am_ids:
                sum_pick_am += pick_am.amount
                self.balance_pick_am = sum_pick_am
            self.balance_inv_stock_cost = sum_inv_am - sum_pick_am
        if self.invoice_cost_am_ids and self.landed_cost_am_ids:
            for invc_am in self.invoice_cost_am_ids:
                sum_invc_am += invc_am.amount
                self.balance_invc_am = sum_invc_am
            for lc_am in self.landed_cost_am_ids:
                sum_lc_am += lc_am.amount
                self.balance_lcost_am = sum_lc_am
            self.balance_invc_lcost = sum_invc_am - sum_lc_am
