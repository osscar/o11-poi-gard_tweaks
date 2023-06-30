# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class PropagateGroupAccountAnalytic(models.Model):
    _name = "propagate.group.account.analytic"

    name = fields.Char("Name", readonly=True)
    description = fields.Char("Description", size=25, help="A short description to identify the group.")
    type = fields.Selection(
        [
            ("purchase", "Purchase Order"),
            ("sale", "Sale Order"),
        ],
        string="Type",
        required=True,
        help="Select order type for group.",
    )
    department_id = fields.Many2one(
        "hr.department",
        string="Parent Account Department",
        help="Select department for order parent analytic account. eg. Purchases / Imports for PO00034",
    )
    account_value_ids = fields.One2many(
        "propagate.group.account.analytic.account",
        "group_id",
        string="Account Values",
        help="Default analytic account values.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    _sql_constraints = [
        ('description_uniq', 'unique (description)',
         'The group description must be unique.')
    ]

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code(
            "propagate.group.account.analytic"
        )
        return super().create(vals)

    # @api.multi
    # def write(self, vals):
    @api.onchange("type")
    def _onchange_type(self):
        # create default order parent analytic account;
        # process is automated; form view field attrs
        # readonly if is_parent == True
        acc_vals = self.account_value_ids
        if not any(a.is_parent == True for a in acc_vals):
            parent_vals = {
                "group_id": self.id,
                "name": "AB#####",
                "code": "AB#####",
                "is_parent": True,
            }
            self.account_value_ids = self.account_value_ids.create(parent_vals)

    @api.multi
    @api.depends("name")
    def name_get(self):
        res = []
        for group in self:
            name = group.name
            description = group.description
            if description:
                name = ": ".join([name, description])
            res.append((group.id, name))
        return res
    
    def button_unlink_account_line(self):
        for line in self.account_value_ids:
            line.unlink()


class PropagateGroupAccountAnalyticAccount(models.Model):
    _name = "propagate.group.account.analytic.account"

    group_id = fields.Many2one(
        "propagate.group.account.analytic",
        string="Group",
        readonly=True,
        ondelete="cascade",
        help="Propagate group related to this account.",
    )
    name = fields.Char(
        string="Name",
        required=True,
    )
    code = fields.Char(
        string="Code",
        size=10,
        required=True,
    )
    is_parent = fields.Boolean(
        string="Order Parent",
        default=False,
        readonly=True,
        help="Select this account as parent account for order.",
    )