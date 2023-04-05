# -*- coding: utf-8 -*-

# import logging

from openerp import models, fields, api, _

# _logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.one
    @api.depends("analytic_account_id")
    def _get_analytic_account(self):
        self.ensure_one()
        if self.analytic_account_id:
            self.analytic_main_tag = self.analytic_account_id.main_tag
            self.analytic_main_tag_parent = self.analytic_account_id.main_tag_parent

    analytic_main_tag = fields.Char(
        "Categoría", compute=_get_analytic_account, store=True
    )
    analytic_main_tag_parent = fields.Char(
        "Categoría raíz", compute=_get_analytic_account, store=True
    )
    analytic_account_department_id = fields.Many2one(
        string="Analytic Account Department",
        related="analytic_account_id.department_id",
        store=True
    )
    analytic_account_parent_id = fields.Many2one(
        string="Analytic Account Parent", related="analytic_account_id.parent_id", store=True
    )
