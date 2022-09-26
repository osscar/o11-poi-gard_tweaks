# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields

# _logger = logging.getLogger(__name__)


class CcDosif(models.Model):
    _inherit = "poi_bol_base.cc_dosif"

    journal_id = fields.Many2one(
        "account.journal",
        related="warehouse_id.journal_id",
        string="Sale Journal",
        readonly=True,
    )
