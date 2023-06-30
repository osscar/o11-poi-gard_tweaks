# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class PropagateCreateAccountAnalytic(models.TransientModel):
    """
    Analytic account creation wizard.
    """

    _name = "propagate.create.account.analytic"
    _description = "Create analytic accounts."

    group_id = fields.Many2one(
        "propagate.group.account.analytic",
        string="Propagate Group",
        help="Select a propagation group to obtain line values, or create line values manually.",
    )
    wizard_line = fields.One2many(
        "propagate.create.account.analytic.line",
        "wizard_id",
        string="Create Values",
        help="These values will be used to create the analytic accounts.",
    )

    def _get_order_ids(self):
        group_id = self.group_id
        order_obj = self.env[str(group_id.type) + ".order"]
        active_ids = self._context.get("active_ids", False)
        order_ids = order_obj.browse(active_ids)
        return order_ids

    @api.multi
    @api.onchange("group_id")
    def onchange_group_id(self):
        if self.group_id:
            vals = {
                "wizard_id": self.id,
            }
            lines = []
            for order in self._get_order_ids():
                for acc_vals in self.group_id.account_value_ids:
                    vals = {
                        "wizard_id": self.id,
                        "is_parent": acc_vals.is_parent,
                        "name": acc_vals.name,
                        "code": order.name + acc_vals.code,
                    }
                    if acc_vals.is_parent == True:
                        vals["department_id"] = self.group_id.department_id.id
                        vals["name"] = order.name
                        vals["code"] = order.name
                    lines += self.wizard_line.create(vals)
            self.wizard_line = [l.id for l in lines]

    @api.multi
    def button_create(self):
        order_ids = self._get_order_ids()
        for order in order_ids:
            analyt_account_obj = self.env["account.analytic.account"]
            lines = self.wizard_line
            vals = {}
            child_ids = []
            for line in lines:
                # if analyt_account_obj.search([("code", "=", line.code)]):
                #     raise ValidationError(
                #         _(
                #             "An analytic account with that name: %s, already exists. Please use that one or delete it, or remove it from the wizard lines, and try again."
                #         )
                #         % (line.name)
                #     )

                vals = {
                    "name": line.name,
                    "code": line.code,
                    "department_id": line.department_id.id,
                }
                result = analyt_account_obj.create(vals)

                if line.is_parent:
                    parent_id = result
                else:
                    child_ids += result
            parent_id = [a.write({"parent_id": parent_id.id}) for a in child_ids]
        return {
            "type": "set_scrollTop",
        }

    def button_unlink_wizard_line(self):
        for line in self.wizard_line:
            line.unlink()
        return {
            "type": "set_scrollTop",
        }


class PropagateCreateAccountAnalyticLine(models.TransientModel):
    _name = "propagate.create.account.analytic.line"
    _description = "Create wizard lines."

    department_id = fields.Many2one(
        "hr.department",
        string="Parent Account Department",
        help="Select the department for the parent analytic account.",
    )
    name = fields.Char(string="Name", help="Analytic account name.")
    code = fields.Char(string="Reference", help="Analytic account code.")
    is_parent = fields.Boolean(
        string="Order Parent",
        default=False,
        readonly=True,
        help="Use this account as order parent analytic account.",
    )
    wizard_id = fields.Many2one(
        "propagate.create.account.analytic",
        string="Create Wizard ID",
        ondelete="cascade",
    )
