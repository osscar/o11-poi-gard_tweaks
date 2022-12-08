from odoo import models, fields, api
from odoo.tools.translate import _


class AccountMoveAnalyticRecreate(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _name = 'account.move.analytic.recreate'
    _description = 'Account move recreate analytic lines'

    @api.multi
    def recreate_move_analytic_lines(self):
        ac_move_ids = self._context.get('active_ids', False)
        res = self.env['account.move'].browse(ac_move_ids)
        aml_ids = [aml for am in res for aml in am.line_ids]
        ret = []
        for aml in aml_ids:
            if aml.analytic_account_id or aml.analytic_tag_ids:
                ret = aml.create_analytic_lines()
                move_ids = aml.move_id
        if ret:
            return {
                'name': _('Recreate Analytic Lines'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'res_ids': move_ids,
                'domain': [('id', 'in', move_ids)],
            }
        return {'type': 'ir.actions.act_window_close'}
