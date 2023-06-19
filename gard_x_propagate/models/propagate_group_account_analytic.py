# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import api, fields, models, _

# from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class PropagateGroupAccountAnalytic(models.Model):
    _name = "propagate.group.account.analytic"

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
        "propagate.group.account.analytic.account",
        "group_id",
        string="Account Values",
        help="Default analytic account values.",
    )
    active = fields.Boolean(string="Active", default=True)

    def button_unlink_account_line(self):
        for line in self.account_value_ids:
            line.unlink()

    # @api.multi
    # def write(self, vals):
    #     res = super().write(vals)
        
    #     # create default order parent analytic account;
    #     # process is automated; form view field attrs
    #     # readonly if is_parent == True
    #     acc_vals = self.account_value_ids
    #     if acc_vals:
    #         if not any(a.is_parent == 'True' for a in acc_vals):
    #             acc_parent_vals = {
    #                 "group_id": self.group_id.id,
    #                 "name": "AB#####",
    #                 "code": "AB#####",
    #                 "is_parent": True,
    #             }
    #             self.account_value_ids.create(acc_parent_vals)

    #     return res


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
    )
    code = fields.Char(
        string="Code",
        size=10,
    )
    is_parent = fields.Boolean(
        string="Order Parent",
        default=False,
        readonly=True,
        help="Parent account for order.",
    )

    # @api.multi
    # @api.depends("name", "code")
    # def name_get(self):
    #     res = []
    #     for record in self:
    #         name = record.group_id.parent_id.name + "/ " + record.name + record.code
    #         res.append((record.id, name))
    #     return res
