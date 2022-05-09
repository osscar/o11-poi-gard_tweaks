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

    is_accountable = fields.Boolean(
        'Accountable',
        copy=False,
        store=True,
        readonly=True)
    move_type = fields.Selection([
        ('is_in', 'In'), ('is_out', 'Out'),
        ('is_dropshipped', 'Dropship'),
        ('is_dropshipped_returned', 'Returned Dropship'),
        ('is_internal', 'Internal')], string='Type',
        compute='_get_move_type',
        copy=False,
        store=True,
        readonly=True,
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
        if self.location_id._should_be_valued() and self.location_dest_id._should_be_valued():
            return True
        return False

    @api.depends('location_id', 'location_dest_id')
    def _get_move_type(self):
        for move in self:
            is_accountable = False
            move_type_id = None
            _logger.debug('move.id >>>: %s', move.id)
            _logger.debug('is_accountable for move >>>: %s' % is_accountable)
            _logger.debug('move_type_id for move >>>: %s' % move_type_id)
            # revise this code - may have bugs
            find_move_type = [
                '_is_in',
                '_is_out',
                '_is_dropshipped',
                '_is_dropshipped_returned',
                '_is_internal'
            ]
            # _logger.debug('find_move_type >>>: %s', find_move_type)
            for move_type in find_move_type:
                _logger.debug('move_type >>>: %s' % move_type)
                move_type_bool = getattr(move, move_type)()
                _logger.debug('move_type_bool >>>: %s' % move_type_bool)
                # mtype_same_use = move.location_id.usage in move.location_dest_id.usage
                # _logger.debug('mtype_same_use >>>: %s' % mtype_same_use)
                # _logger.debug('mtype l usage >>>: %s' % move.location_id.usage)
                # _logger.debug('mtype l_dest usage >>>: %s' % move.location_dest_id.usage)
                # _logger.debug('is_accountable >>>: %s' % is_accountable)
                if move_type_bool:
                    move_type_id = move_type[1:]
                    _logger.debug('move_type_id >>>: %s' % move_type_id)
                    if move_type != ('_is_internal'):
                        is_accountable = True
            _logger.debug('move_type_id end >>>: %s' % move_type_id)
            _logger.debug('is_accountable end >>>: %s' % is_accountable)
            move.move_type = move_type_id
            move.write({'is_accountable': is_accountable})
