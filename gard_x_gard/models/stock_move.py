# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
# from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

# import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    _order = 'date desc'

    move_type = fields.Selection([
        ('is_in', 'In'), ('is_out', 'Out'),
        ('is_dropshipped', 'Dropship'),
        ('is_dropshipped_returned', 'Returned Dropship'),
        ('is_internal', 'Internal')], string='Type',
        compute='_get_move_type', copy=False,
        index=True, store=True, readonly=True,
        help="* In: Incoming stock (accountable).\n"
             "* Out: Outgoing stock (accountable).\n"
             "* Dropship: Dropshipped (accountable).\n"
             "* Dropship: Returned dropship (accountable).\n"
             "* Internal: Internal moves (not accountable).")

    requested_by = fields.Many2one(
        'res.users', 'Requested By', readonly=True,
        help="User that requested this move.")

    @api.model
    def create(self, vals):
        res = super(StockMove, self).create(vals)

        res.update({'requested_by': self._context.get('uid')})
        return res

    @api.multi
    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()

        res['requested_by'] = self.requested_by.id
        return res

    def _is_internal(self):
        if self.location_id._should_be_valued() and self.location_dest_id._should_be_valued():
            return True
        return False

    @api.multi
    def _get_move_type(self):
        for move in self:
            find_move_type = ["_is_in", "_is_out", "_is_dropshipped", "_is_dropshipped_returned", "_is_internal"]
            # _logger.debug('find_move_type >>>: %s', find_move_type)

            for move_type in find_move_type:
                # _logger.debug('move_type >>>: %s', move_type)
                if getattr(move, move_type)() == True:
                    move.move_type = move_type[1:]
                    # _logger.debug('move_type compute >>>: %s', move_type)
