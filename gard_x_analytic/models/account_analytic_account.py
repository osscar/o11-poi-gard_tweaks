# -*- coding: utf-8 -*-

from odoo import api, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    _sql_constraints = [
        ('uniq_code', 'UNIQUE (code)', _('The analytic account code must be unique.'))
    ]
        
    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=30):
        if not args:
            args = []
        if name:
            domain = [
                "|",
                "|",
                "|",
                ("name", operator, name),
                ('code', operator, name),
                ("parent_id.name", operator, name),
                ("department_id.name", operator, name)
            ]
            accounts = self.search(domain + args, limit=limit, )
            res = accounts.name_get() or []
            if res:
                if limit:
                        limit_rest = limit - len(accounts)
                else:
                    limit_rest = limit
                if limit_rest or not limit:
                    args += [('id', 'not in', accounts.ids)]
                    res += super().name_search(
                        name, args=args, operator=operator, limit=limit_rest)
                return res
        return super().name_search(
            name, args=args, operator=operator, limit=limit
        )

    @api.multi
    @api.depends("name")
    def name_get(self):
        res = []
        for account in self:
            res = super(AccountAnalyticAccount, account).name_get()
            name = account.name
            code = account.code
            if code:
                name = ": ".join([name, code])
            res.append((account.id, name))
        return res

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        parent_acc = self.parent_id

        # get department from parent
        if parent_acc and parent_acc.department_id:
            self.department_id = parent_acc.department_id
