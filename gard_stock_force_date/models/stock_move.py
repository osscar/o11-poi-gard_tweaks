# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime
from collections import defaultdict
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    # override method to use force_date value for accounting entries
    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        AccountMove = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity
        ref = self.picking_id.name
        if self.env.context.get('force_valuation_amount'):
            if self.env.context.get('forced_quantity') == 0:
                ref = 'Revaluation of %s (negative inventory)' % ref
            elif self.env.context.get('forced_quantity') is not None:
                ref = 'Correction of %s (modification of past move)' % ref
        move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value),
            credit_account_id, debit_account_id)
        if self.picking_id.force_date != False:
            if move_lines:
                # use f_date for accounting entries date
                f_date = datetime.strptime(self.picking_id.force_date, '%Y-%m-%d %H:%M:%S')
                company = self.company_id
                curr_sec_id = company.currency_id_sec
                if not company:
                    company = self.env.user.company_id
                    curr_sec_id = company.currency_id_sec
                new_account_move = AccountMove.sudo().create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': f_date,
                    'ref': ref,
                    'stock_move_id': self.id,
                })
                if self.picking_id:
                    self.picking_id.move_id = new_account_move.id
                elif self.inventory_id:
                    self.inventory_id.move_id = new_account_move.id
                new_account_move.post()
        else:
            return super(StockMove, self)._create_account_move_line(credit_account_id, debit_account_id, journal_id)

    # inherit method to use force_date for stock move date
    def _action_done(self):
        self.product_price_update_before_done()
        res = super(StockMove, self)._action_done()

        f_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        for move in self:
            if move.picking_id.force_date:
                f_date = move.picking_id.force_date
                self.write({'state': 'done', 'date': f_date})
        return res


