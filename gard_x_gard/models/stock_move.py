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

    is_accountable = fields.Boolean('Accountable', compute='_get_move_type',
        copy=False, index=True, readonly=True)
    move_type = fields.Selection([
        ('is_in', 'In'), ('is_out', 'Out'),
        ('is_dropshipped', 'Dropship'),
        ('is_dropshipped_returned', 'Returned Dropship'),
        ('is_internal', 'Internal')], string='Type',
        compute='_get_move_type', copy=False, index=True, readonly=True,
        help="* In: Incoming stock.\n"
             "* Out: Outgoing stock.\n"
             "* Dropship: Dropshipped.\n"
             "* Dropship: Returned dropship.\n"
             "* Internal: Internal moves.")

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
        # _logger.debug('_is_internal self.location_id >>>: %s', self.location_id._should_be_valued())
        # _logger.debug('_is_internal self.location_dest_id >>>: %s', self.location_dest_id._should_be_valued())
        # _logger.debug('_is_internal ?? >>>: %s', self.location_id._should_be_valued() and self.location_dest_id._should_be_valued())
        if self.location_id._should_be_valued() and self.location_dest_id._should_be_valued():
            return True
        return False

    @api.depends('move_type', 'is_accountable')
    @api.multi
    def _get_move_type(self):
        for move in self:
            is_accountable = False
            move_type = False
            if move._is_in():
                move_type = 'is_in'
                is_accountable = True
            if move._is_out():
                move_type = 'is_out'
                is_accountable = True
            if move._is_dropshipped():
                move_type = 'is_dropshipped'
                is_accountable = True
            if move._is_dropshipped_returned():
                move_type = 'is_dropshipped_returned'
                is_accountable = True
            if move._is_internal():
                move_type = 'is_internal'
                is_accountable = False
            move.move_type = move_type
            move.is_accountable = is_accountable

            # revise this code - has bugs, above used instead until resolved; this is shorter
            # find_move_type = ['_is_in', '_is_out', '_is_dropshipped', '_is_dropshipped_returned', '_is_internal']
            # # _logger.debug('find_move_type >>>: %s', find_move_type)
            #
            # for move_type in find_move_type:
            #     _logger.debug('move_type >>>: %s' % move_type)
            #     move_type_bool = getattr(move, move_type)()
            #     _logger.debug('move_type_bool >>>: %s' % move_type_bool)
            #     if move_type_bool == True:
            #         # _logger.debug('_is_internal >>>: %s', move_type == '_is_internal')
            #         if move_type != '_is_internal':
            #             is_accountable = True
            #         move.move_type = move_type[1:]
            #         move.is_accountable = is_accountable
            #         _logger.debug('move_type compute >>>: %s', move_type)
