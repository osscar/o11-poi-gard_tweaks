# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from email.policy import default
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

    # propagate route over sale order lines
    @api.onchange('route_id')
    @api.multi
    def _propagate_route_id(self):
        for line in self.order_line:
            line.route_id = self.route_id

    # unnecessary validation: procurement rule validation takes care of this
    # @api.multi
    # def _action_confirm(self):
    #     res = super(SaleOrder, self)._action_confirm()
    #     for line in self.mapped('order_line'):
    #         if not line.route_id :
    #             raise ValidationError(_("Please select appropriate routes for all sale ordr lines."))
    #     return res

    # @api.depends('state')
    # def _check_team_id(self):
    #     if not self.team_id:
    #         _logger.info('team_id: %s', self.team_id)
    #         raise ValidationError(_('Please select a sales channel.'))

    @api.multi
    def write(self, values):
        model = request.params.get('model')
        method = request.params.get('method')
        # action_auth_intcon = request.params.get('method') in 'action_auth_internal_consumption'
        action_confirm = model in 'sale.order' and method in 'action_confirm'
        action_cancel = model in 'sale.order' and method in 'action_cancel'
        action_draft = model in 'sale.order' and method in 'action_draft'
        send_mail_action = model in 'mail.compose.message' and method in 'send_mail_action'
        allow_write = action_confirm or action_cancel or action_draft or send_mail_action
        # action_auth_intcon or: unused for now
        # _logger.debug('Requested params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        # _logger.debug('state >>>>: %s', self.mapped('state'))
        # _logger.info('values: %s', values)
        if any(state != 'draft' for state in set(self.mapped('state')) if not allow_write):
            raise UserError(_('Edit allowed only in draft state. [%s.%s]' % (request.params.get('model'), request.params.get('method'))))
        else:
            return super().write(values)
            # _logger.info('Written values: %s', values)
 
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        # _logger.debug('aic >>>>: %s', self)
        inv_ids = super(SaleOrder, self).action_invoice_create(grouped=grouped, final=final)
        invoice_obj = self.env['account.invoice']
        for inv in invoice_obj.browse(inv_ids):
            # _logger.debug('aic >>>>: %s', self)
            # inherited to set nit and razon field values from partner_invoice_id
            inv.write({
                'nit': self.partner_invoice_id.nit or self.partner_invoice_id.ci,
                'razon': self.partner_invoice_id.razon,
                'contract_nr': self.contract_nr,
            })
        return inv_ids
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    date_order_id = fields.Datetime('Order Date', 
                                    related='order_id.date_order', 
                                    store=True, 
                                    readonly=True, 
                                    index=True)

    @api.multi
    def write(self, values):
        # write restrictions when not in draft
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

    @api.onchange('product_id')
    def _onchange_product_id_propagate_route(self):
        self.route_id = self.order_id.route_id