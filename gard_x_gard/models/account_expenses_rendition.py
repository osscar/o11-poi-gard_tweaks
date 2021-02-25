##############################################################################
#
#    Odoo Module
#    Copyright (C) 2015 Grover Menacho (<http://www.grovermenacho.com>).
#    Copyright (C) 2015 Poiesis Consulting (<http://www.poiesisconsulting.com>).
#    Autor: Grover Menacho
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, modules, api, _
from odoo.exceptions import Warning, ValidationError, UserError

class AccountExpensesRendition(models.Model):
    _inherit = 'account.expenses.rendition'

    state = fields.Selection([('draft','Draft'),
                              ('confirmed','Confirmed'),
                              ('done','Done'),
                              ('cancel', 'Canceled')],
                              'State', default='draft', track_visibility='always')
    rendition_invoice_ids = fields.One2many('account.expenses.rendition.invoice',
        'rendition_id','Invoices', copy=True, track_visibility='always')

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default.update({'name': False})
        return super(AccountExpensesRendition, self).copy(default)

    @api.multi
    def write(self, vals):
        if any(state != 'draft' for state in set(self.mapped('state'))
            if not self.env.user.has_group('gard_x_gard.group_account_edit')):
            raise UserError(_("Edit allowed only in draft state."))
        else:
            return super().write(vals)

class AccountExpensesRenditionInvoice(models.Model):
    _name = 'account.expenses.rendition.invoice'
    _inherit = ['account.expenses.rendition.invoice', 'mail.thread']

    rendition_move_id = fields.Many2one(related='rendition_id.move_id', string="Asiento")
    payment_request_id = fields.Many2one(related='rendition_id.payment_request_id',
        string="Solicitud de Pago")
    state = fields.Selection(related='rendition_id.state', string='Estado doc',
        readonly=True, store=True, default='draft', track_visibility='always')

    @api.multi
    def write(self, vals):
        if any(state != 'draft' for state in set(self.mapped('state'))
            if not self.env.user.has_group('gard_x_gard.group_account_edit')):
            raise UserError(_("Edit allowed only in draft state."))
        else:
            return super().write(vals)
