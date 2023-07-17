# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import fields, models, _

# _logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = "account.journal"

    code = fields.Char(
        string="Short Code",
        size=10,
        required=True,
        help="The journal entries of this journal will be named using this prefix.",
    )
    note = fields.Text("Description")