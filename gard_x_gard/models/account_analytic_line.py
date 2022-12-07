# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

# from math import copysign


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
