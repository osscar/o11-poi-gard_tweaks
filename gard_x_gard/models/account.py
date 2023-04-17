# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.http import request

import odoo.addons.decimal_precision as dp

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


# class AccountMove(models.Model):
#     _inherit = "account.move"
