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
    account_analytic_default_ids = fields.One2many(
        "account.analytic.propagate.group.account",
        "group_id",
        string="Analytic Accounts",
        help="Default analytic account details.",
    )
    parent_id = fields.Many2one(
        "account.analytic.account",
        string="Parent Analytic Account",
        help="Parent analytic account for group.",
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
    group_id = fields.Many2one(
        "account.analytic.propagate.group",
        string="Group",
        ondelete="cascade",
        help="Propagate group related to this account.",
    )
