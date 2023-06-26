# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import fields, models, _

# _logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "date_done desc, create_date desc"

    requested_by = fields.Many2one(
        "res.users",
        "Requested By",
        readonly=True,
        help="User that requested this transfer.",
    )
