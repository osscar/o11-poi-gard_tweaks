# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import fields, models, _

# _logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    code = fields.Char(
        "Short Name",
        required=True,
        size=10,
        help="Short name used to identify your warehouse",
    )
