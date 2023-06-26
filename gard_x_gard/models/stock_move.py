# # -*- coding: utf-8 -*-
# # Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# _logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    _order = 'date desc'

    is_accountable = fields.Boolean(
        'Accountable',
        compute='_is_accountable',
        copy=False,
        store=True,
        readonly=True
    )
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

    @api.depends('state', 'location_id', 'location_dest_id')
    def _get_move_type(self):
        for move in self:
            move_type_id = None
            # _logger.debug('move.id >>>: %s', move.id)
            find_move_type = [
                '_is_in',
                '_is_out',
                '_is_dropshipped',
                '_is_dropshipped_returned',
                '_is_internal'
            ]
            for move_type in find_move_type:
                # _logger.debug('move_type >>>: %s' % move_type)
                move_type_bool = getattr(move, move_type)()
                if move_type_bool:
                    move_type_id = move_type[1:]
            # _logger.debug('move_type_id end >>>: %s' % move_type_id)
            move.move_type = move_type_id

    @api.depends('state', 'move_type')
    def _is_accountable(self):
        for move in self:
            is_accountable = False
            if move.move_type:
                if move.move_type != 'is_internal':
                    is_accountable = True
            move.is_accountable = is_accountable