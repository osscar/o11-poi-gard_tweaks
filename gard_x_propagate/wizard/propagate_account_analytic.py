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
        order_obj = self.env[str(group_id.type + ".order")]
        active_ids = self._context.get("active_ids", False)
        order_ids = order_obj.browse(active_ids)
        return order_ids

    @api.onchange("group_id")
    def onchange_group_id(self):
        if self.group_id:
            for order in self._get_order_ids():
                for acc_vals in self.group_id.account_value_ids:
                    vals = {
                        "wizard_id": self.id,
                        "is_parent": acc_vals.is_parent,
                        "name": acc_vals.name,
                        "code": acc_vals.code,
                    }
                    if acc_vals.is_parent == True:
                        vals["parent_id"] = self.group_id.parent_id
                        vals["name"] = order.name
                        vals["code"] = order.code
                self.wizard_line.create(vals)

    @api.multi
    def button_create(self):
        analyt_account_obj = self.env["account.analytic.account"]
        res = analyt_account_obj.create(vals)
        order_ids = self._get_order_ids()
        for order in order_ids:
            # _logger.debug("bcaa order >>>: %s", order)
            for line in self.wizard_line:
                if analyt_account_obj.search([("name", "=", line.name)]):
                    raise ValidationError(
                        _(
                            "An analytic account with that name: %s, already exists. Please use that one or delete it, and try again."
                        )
                        % (line.name)
                    )
                vals = {
                    "name": line.name,
                    "code": line.code,
                }
                if line.is_parent:
                    vals["parent_id"] = line.parent_id.id
                parent_vals = res
                res["parent_id"] = parent_vals
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
    _order = "parent_id desc, name desc"

    parent_id = fields.Many2one(
        "account.analytic.account",
        string="Parent Analytic Account",
        help="Order reference name is used for this analytic account's name.",
    )
    name = fields.Char(string="Name", help="Analytic account name.")
    code = fields.Char(string="Reference", help="Analytic account code.")
    wizard_id = fields.Many2one(
        "propagate.create.account.analytic",
        string="Create Wizard ID",
        ondelete="cascade",
    )
