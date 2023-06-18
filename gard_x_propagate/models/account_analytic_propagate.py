# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class AccountAnalyticPropagateGroup(models.Model):
    name = "account.analytic.propagate.group"

    name = fields.Char("Name", required=True)
    type = fields.Selection(
        [
            ("purchase", "Purchase Order"),
            ("sale", "Sale Order"),
        ],
        string="Type",
        required=True,
        help="Select order type for group.",
    )
    parent_id = fields.Many2one(
        "account.analytic.account",
        string="Parent Analytic Account",
        help="Select parnet analytic account for the order parent analytic account. eg. Purchases / Imports for PO00034",
    )
    account_value_ids = fields.One2many(
        "account.analytic.propagate.group.account",
        "group_id",
        string="Account Values",
        help="Default analytic account values.",
    )
    active = fields.Boolean(string="Active", default=True)

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        
        # create default order parent analytic account;
        # process is automated; form view field attrs
        # readonly if is_parent == True
        acc_parent_vals = {
            "group_id": self.group_id.id,
            "name": "AB#####",
            "code": "AB#####",
            "is_parent": True,
        }
        self.account_value_ids.create(acc_parent_vals)

        return res


class AccountAnalyticPropagateGroupAccount(models.Model):
    name = "account.analytic.propagate.group.account"

    group_id = fields.Many2one(
        "account.analytic.propagate.group",
        string="Group",
        readonly=True,
        ondelete="cascade",
        help="Propagate group related to this account.",
    )
    name = fields.Char(
        "Name",
    )
    code = fields.Char(
        "Code",
        size=10,
    )
    is_parent = fields.Boolean(
        string="Order Parent",
        default=False,
        readonly=True,
        help="Parent account for order.",
    )

    @api.multi
    @api.depends("name", "code")
    def name_get(self):
        res = []
        for record in self:
            name = group_id.parent_id.name + "/ " + record.name + record.code
            res.append((record.id, name))
        return res
