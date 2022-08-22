# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

import odoo.addons.decimal_precision as dp

# _logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    team_id = fields.Many2one('crm.team', 
                              'Sales Channel', 
                              change_default=False, 
                              default=False, 
                              track_visibility='onchange')
    route_id = fields.Many2one('stock.location.route', 
                               string='Propagate Route', 
                               domain=[('sale_selectable', '=', True)])

    # propagate route over sale order lines
    @api.onchange('route_id')
    @api.multi
    def _propagate_route_id(self):
        for line in self.order_line:
            line.route_id = self.route_id

    # @api.depends('state')
    # def _check_team_id(self):
    #     if not self.team_id:
    #         _logger.info('team_id: %s', self.team_id)
    #         raise ValidationError(_('Please select a sales channel.'))

    @api.multi
    def write(self, values):
        action_auth_intcon = request.params.get('method') in 'action_auth_internal_consumption'
        action_confirm = request.params.get('method') in 'action_confirm'
        action_cancel = request.params.get('method') in 'action_cancel'
        action_draft = request.params.get('method') in 'action_draft'
        allow_write = action_auth_intcon or action_confirm or action_cancel or action_draft
        # _logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        # _logger.debug('state >>>>: %s', self.mapped('state'))
        # _logger.info('values: %s', values)
        if any(state != 'draft' for state in set(self.mapped('state')) if not allow_write):
            raise UserError(_('Edit allowed only in draft state. [%s.%s]' % (request.params.get('model'), request.params.get('method'))))
        else:
            return super().write(values)
            # _logger.info('Written values: %s', values)

    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _get_default_route_id(self):
        domain = [('sale_selectable', '=', True)]
        return self.env['stock.location.route'].search(domain, limit=1, order='id').id

    date_order_id = fields.Datetime('Order Date', 
                                    related='order_id.date_order', 
                                    store=True, 
                                    readonly=True, 
                                    index=True)
    route_id = fields.Many2one('stock.location.route', 
                               string='Route', 
                               default=_get_default_route_id,
                               domain=[('sale_selectable', '=', True)], 
                               ondelete='restrict')

    @api.multi
    def write(self, values):
        immediate_transfer_process = request.params.get('method') in 'immediate.transfer.process'
        allow_write = immediate_transfer_process
        # _logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        # _logger.debug('state >>>: %s', self.mapped('state'))
        # _logger.info('self: %s', self)
        if any(state != 'draft' for state in set(self.mapped('state')) if not allow_write):
            raise UserError(_('Edit allowed only in draft state. [%s.%s]' % (request.params.get('model'), request.params.get('method'))))
        else:
            return super().write(values)
            # _logger.info('Written values: %s', values)
