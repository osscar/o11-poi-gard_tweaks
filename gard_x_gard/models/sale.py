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

    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=False, default=False, required=True, copy=False, track_visibility='onchange')

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
