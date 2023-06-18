# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class AccountAnalyticPropagateCreate(models.TransientModel):
    """
    Analytic account creation wizard.
    """

    _name = "account.analytic.propagate.create.wizard"
    _description = "Create analytic accounts."

    group_id = fields.Many2one(
        "account.analytic.propagate.group",
        string="Group",
        help="Select a propagation group to obtain line values, or create line values manually.",
    )
    account_analytic_default_id = fields.Many2one(
        "account.analytic.account",
        string="Default Analytic Account",
        help="Select the default analytic account for order. This account will be set as default for the order lines.",
    )
    wizard_line = fields.Many2one(
        "account.analytic.propagate.create.wizard.line",
        string="Create Values",
        ondelete="cascade",
        help="These values will be used to create the analytic accounts.",
    )
    
    @api.onchange("group_id")
    def onchange_group_id(self):
        group_id = self.group_id
        order_obj = self.env[str(group_id.type + '.order')]
        active_ids = self._context.get("active_ids", False)
        order_ids = order_obj.browse(active_ids)

        for order in order_ids:
            for acc_vals in self.group_id.account_value_ids:
                parent_id = False
                vals = {
                        "wizard_id": self.id,
                        "parent_id": parent_id,
                        "name": acc_vals.name,
                        "code": acc_vals.code,
                    }
                if acc_vals.is_parent == True:
                    vals["parent_id"] = group_id.parent_id
                    vals["name"] = order.name
                    vals["code"] = order.code
            self.wizard_line.create(vals)
            [line.write({"parent_id": [pline.id for pline in line if pline.parent_id != False]}) for line in self.wizard_line]


        # purchase_order_ids = self._context.get("active_ids", False)
        # res = self.env["purchase.order"].browse(purchase_order_ids)
        # # acc_default_id = ["1_cp", "2_cd", "3_oc", "4_pg", "5_ivacf"]
        # acc_default_id = [1, 2, 3, 4, 5]
        # acc_default_name = [
        #     "Costos Producto",
        #     "Costos Directos",
        #     "Otros Costos",
        #     "Pagos",
        #     "Credito Fiscal IVA",
        # ]
        # acc_default_code = ["/CP", "/CD", "/OC", "/PG", "/IVACF"]
        # acc_default = {}
        # for di, dn, dc in zip(acc_default_id, acc_default_name, acc_default_code):
        #     acc_default[di] = {"name": dn, "code": dc}
        #     # _logger.debug("bclidv acc_default >>>: %s", (acc_default))
        #     # _logger.debug("bclidv acc_default >>>: %s", (list(acc_default)))
        # for order in res:
        #     # _logger.debug("bclidv order >>>: %s", (order))
        #     hr_department_obj = self.env["hr.department"]
        #     acc_parent_default_department = hr_department_obj.search([('display_name', "=", acc_parent_default_department)]).id
        #     analyt_acc_obj = self.env["account.analytic.account"]
        #     analyt_acc_parent_vals = {"name": order.name,
        #                               "department_id": acc_parent_default_department}
        #     account_analytic_parent_id = analyt_acc_obj.search([('name', "=", order.name)]).id
        #     if not self.account_analytic_parent_id:
        #         if analyt_acc_obj.search([("name", "=", order.name)]):
        #             raise ValidationError(
        #                 _(
        #                     "An analytic tag with that name: %s, already exists. Please use that one or delete it, and try again."
        #                 ) % (order.name)
        #             )
        #         analyt_tag_create = analyt_tag_obj.create(analyt_tag_vals)
        #         self.tag_id = analyt_tag_create
        #     # _logger.debug("bclidv self.tag_id >>>: %s", (self.tag_id))
        #     for acc in acc_default:
        #         # _logger.debug("bclidv acc >>>: %s", (acc_default[acc]["name"]))
        #         vals = {
        #             "wizard_id": self.id,
        #             "parent_id": acc.,
        #             "name": acc_default[acc]["name"] + " (" + order.name + ")",
        #             "code": order.name + acc_default[acc]["code"],
        #         }
        #         self.line_ids.create(vals)
        # return {
        #     "type": "set_scrollTop",
        # }

    @api.one
    def button_create_analytic_account(self):
        analyt_account_obj = self.env["account.analytic.account"]
        purchase_ids = self._context.get("active_ids", False)
        res = self.env["purchase.order"].browse(purchase_ids)
        for order in res:
            # _logger.debug("bcaa order >>>: %s", order)
            for line in self.line_ids:
                if analyt_account_obj.search([("name", "=", line.name)]):
                    raise ValidationError(
                        _(
                            "An analytic account with that name: %s, already exists. Please use that one or delete it, and try again."
                        ) % (line.name)
                    )

                analyt_acc_vals = {
                    "name": line.name,
                    "tag_ids": line.tag_id,
                    "code": line.code,
                }

                if line.create_wizard_id.order_account_line == line:
                    # _logger.debug("bcaa if line oal>>>: %s", (line))
                    order["account_analytic_id"] = order.account_analytic_id.create(acc_analyt_vals)
                else:
                    # _logger.debug("bcaa else >>>: %s", (line))
                    analyt_account_obj.create(acc_analyt_vals)
        return {
            "type": "set_scrollTop",
        }

    def button_unlink_wizard_line(self):
        for line in self.line_ids:
            line.unlink()
        return {
            "type": "set_scrollTop",
        }


class PurchaseOrderAccountAnalyticCreateLine(models.TransientModel):
    """
    Purchase Order analytic account creation wizard line.
    """

    _name = "account.analytic.propagate.create.wizard.line"
    _description = "Create wizard lines."
    # _rec_name = "name"

    parent_id = fields.Many2one(
        "account.analytic.account",
        string="Parent Analytic Account",
        help="Order reference name is used for this analytic account's name."
    )
    # order_name = fields.Char(string="Order Name", help="Order reference name.")
    name = fields.Char(string="Name", help="Analytic account name.")
    code = fields.Char(string="Reference", help="Analytic account code.")
    wizard_id = fields.Many2one(
        "purchase.order.account.analytic.create",
        string="Create Wizard ID",
        ondelete="cascade",
    )
