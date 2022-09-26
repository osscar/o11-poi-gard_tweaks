# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields, _

# _logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    journal_id = fields.Many2one(
        "account.journal",
        string="Sale Journal",
        default=False,
        copy=False,
        domain="[('type', '=', 'sale')]",
    )
