# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, models, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class AccountAnalyticPropagateGroup(models.Model):
    _inherit = "account.analytic.propagate.group"

    name = fields.Char("Name", required=True)
    type = fields.Selection(
        [
            ("purchase", "Purchase Order"),
            # ("sale", "Sale Order"),
        ],
        string="Type",
        required=True,
        help="Select order type for group.",
    )
    account_analytic_default_ids = fields.Many2many(
        "account.analytic.propagate.group.account",
        string="Analytic Accounts",
        help="Default analytic account details.",
    )
    parent_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Parent Analytic Account",
    )
    active = fields.Boolean(string="Active", default=True)


class AccountAnalyticPropagateGroupAccount(models.Model):
    _inherit = "account.analytic.propagate.group.account"

    name = fields.Char(
        "Name",
        required=True,
    )
    code = fields.Char(
        "Code",
        size=10,
        required=True,
    )
