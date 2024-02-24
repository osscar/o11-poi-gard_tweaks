# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"
    _rec_name = "move_id"

    # @api.multi
    # def name_get(self):
    #     result = []
    #     orig_name = dict(super().name_get())
    #     for line in self:
    #         name = orig_name[line.id]
    #         if self.account_:
    #             name = "[%s] %s (%s)" % (line.order_id.name, name,
    #                                      line.order_id.state)
    #         result.append((line.id, name))
    #     return result

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
            res = lines.name_get()
            if limit:
                limit_rest = limit - len(lines)
            else:
                limit_rest = limit
            if limit_rest or not limit:
                args += [('id', 'not in', lines.ids)]
                res += super().name_search(
                    name, args=args, operator=operator, limit=limit_rest)
            return res
        return super().name_search(
            name, args=args, operator=operator, limit=limit
        )
        
    @api.multi
    @api.depends("general_account_id")
    def _get_tag(self):
        for aal in self:
            for tag in aal.account_id.tag_ids:
                aal.analytic_main_tag = tag.display_name
                aal.analytic_main_tag_parent = tag.parent_id.display_name

    analytic_main_tag = fields.Char("Categoría", compute=_get_tag, store=True)
    analytic_main_tag_parent = fields.Char(
        "Categoría raíz", compute=_get_tag, store=True
    )
    analytic_account_parent_id = fields.Many2one(
        string="Analytic Account Parent", related="account_id.parent_id", store=True
    )
