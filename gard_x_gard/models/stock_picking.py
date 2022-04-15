# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
# from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

# import odoo.addons.decimal_precision as dp

# _logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'create_date desc'

    requested_by = fields.Many2one(
        'res.users', 'Requested By', readonly=True,
        help="User that requested this transfer.")
