# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
# from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

# import odoo.addons.decimal_precision as dp

# _logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'
    _order = 'date desc'

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
