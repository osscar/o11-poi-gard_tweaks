# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _rec_name = "move_id"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                "|",
                ("name", operator, name),
                ("account_id.name", operator, name),
                ("move_id.name", operator, name),
            ]
        lines = self.search(domain + args, limit=limit)
        return lines.name_get()

    @api.one
    @api.depends("account_id.tag_ids")
    def _get_tag(self):
        self.ensure_one()
        for tag in self.account_id.tag_ids:
            self.analytic_main_tag = tag.display_name
            self.analytic_main_tag_parent = tag.parent_id.display_name

    analytic_main_tag = fields.Char("Categoría", compute=_get_tag, store=True)
    analytic_main_tag_parent = fields.Char(
        "Categoría raíz", compute=_get_tag, store=True
    )
    analytic_account_parent_id = fields.Many2one(
        string="Analytic Account Parent", related="account_id.parent_id", store=True
    )
