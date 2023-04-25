# -*- coding: utf-8 -*-
# import logging

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class PurchaseOrderAccountAnalyticCreate(models.TransientModel):
    """
    Purchase Order analytic account creation wizard.
    """

    _name = "purchase.order.account.analytic.create"
    _description = "Create analytic accounts."

    line_ids = fields.One2many(
        "purchase.order.account.analytic.create.line",
        "create_wizard_id",
        string="Wizard Lines",
    )
    
    # order_account_line = fields.Many2one(
    #     "purchase.order.account.analytic.create.line",
    #     string="Order Analytic Account Line",
    #     ondelete="cascade",
    #     help="Add analytic account to order.",
    # )

    def button_create_line_default_values(self):
        purchase_order_ids = self._context.get("active_ids", False)
        res = self.env["purchase.order"].browse(purchase_order_ids)
        # acc_default_id = ["0_prnt","1_cp", "2_cd", "3_oc", "4_pg", "5_ivacf"]
        acc_parent_default_department = "Compras / Importaciones"
        acc_default_id = [1, 2, 3, 4, 5]
        acc_default_name = [
            "Costos Producto",
            "Costos Directos",
            "Otros Costos",
            "Pagos",
            "Credito Fiscal IVA",
        ]
        acc_default_code = ["/CP", "/CD", "/OC", "/PG", "/IVACF"]
        acc_default = {}
        for di, dn, dc in zip(acc_default_id, acc_default_name, acc_default_code):
            acc_default[di] = {"name": dn, "code": dc}
            # _logger.debug("bclidv acc_default >>>: %s", (acc_default))
            # _logger.debug("bclidv acc_default >>>: %s", (list(acc_default)))
        for order in res:
            # _logger.debug("bclidv order >>>: %s", (order))
            hr_department_obj = self.env["hr.department"]
            acc_parent_default_department = hr_department_obj.search([('display_name', "=", acc_parent_default_department)]).id
            analyt_acc_obj = self.env["account.analytic.account"]
            analyt_acc_parent_vals = {"name": order.name,
                                      "department_id": acc_parent_default_department}
            if not self.account_analytic_parent_id:
                if analyt_acc_obj.search([("name", "=", order.name)]):
                    raise ValidationError(
                        _(
                            "A parent analytic account with that name: %s, already exists. Please use that one or delete it, and try again."
                        ) % (order.name)
                    )
                analyt_acc_parent_create = analyt_acc_obj.create(analyt_acc_parent_vals)
                self.account_analytic_parent_id = analyt_acc_parent_create
            # _logger.debug("bclidv self.tag_id >>>: %s", (self.tag_id))
            for acc in acc_default:
                # _logger.debug("bclidv acc >>>: %s", (acc_default[acc]["name"]))
                vals = {
                    "create_wizard_id": self.id,
                    "order_name": order.name,
                    "name": acc_default[acc]["name"] + " (" + order.name + ")",
                    "code": order.name + acc_default[acc]["code"],
                    "account_analytic_department_id": self.account_analytic_department_id.id,
                    "account_analytic_parent_id": self.account_analytic_parent_id.id,
                }
                self.line_ids.create(vals)
            # self.order_account_line = self.line_ids[0]
        return {
            "type": "set_scrollTop",
        }

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
                # _logger.debug("bcaa line >>>: %s", line)
                analyt_acc_vals = {
                    "name": line.name,
                    "code": line.code,
                    "parent_id": line.account_analytic_parent_id,
                }

                # if line.create_wizard_id.order_account_line == line:
                #     # _logger.debug("bcaa if line oal>>>: %s", (line))
                order["account_analytic_id"] = self.account_analytic_parent_id
                analyt_account_obj.create(analyt_acc_vals)
                # order.account_analytic_id.create(acc_analyt_vals)
                # else:
                #     # _logger.debug("bcaa else >>>: %s", (line))
                #     analyt_account_obj.create(acc_analyt_vals)
        return {
            "type": "set_scrollTop",
        }

    def button_wizard_line_unlink(self):
        # self.order_account_line = False
        for line in self.line_ids:
            line.unlink()
        return {
            "type": "set_scrollTop",
        }


class PurchaseOrderAccountAnalyticCreateLine(models.TransientModel):
    """
    Purchase Order analytic account creation wizard line.
    """

    _name = "purchase.order.account.analytic.create.line"
    _description = "Creation wizard lines."
    _rec_name = "name"

    order_name = fields.Char(string="Order Name", help="Name for analytic account.")
    name = fields.Char(string="Name", help="Name for analytic account.")
    code = fields.Char(string="Reference", help="Code for analytic account.")
    account_analytic_department_id = fields.Many2one(
        "account.analytic.department",
        string="Analytic Account Department",
    )
    account_analytic_parent_id = fields.Many2one(
        "account.analytic.account",
        string="Parent Analytic Account",
    )
    create_wizard_id = fields.Many2one(
        "purchase.order.account.analytic.create",
        string="Create Wizard ID",
        ondelete="cascade",
    )
