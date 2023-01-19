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

# import logging

from odoo import models, fields, api, _
from odoo.http import request

from odoo.exceptions import UserError

# _logger = logging.getLogger(__name__)


class AccountExpensesRendition(models.Model):
    _inherit = 'account.expenses.rendition'

    @api.multi
    def write(self, vals):
        req_model = request.params.get("model")
        req_method = request.params.get("method")

        action_draft = req_model == ('account.expenses.rendition') and req_method == ('action_draft')
        action_validate = req_model == ('account.expenses.rendition') and req_method == ('action_validate')
        action_approve = req_model == ('account.expenses.rendition') and req_method == ('action_approve')
        action_cancel = req_model == ('account.expenses.rendition') and req_method == ('action_cancel')
        write = req_model == ('account.expenses.rendition') and req_method == ('write')
        action_add_items = req_model == ('account.payment.expenses.wiz') and req_method == ('action_add_items')
        # group_account_edit = self.env.user.has_group('gard_x_gard.group_account_edit')
        allow_write = action_draft or action_validate or action_approve or action_cancel or action_add_items or write
        # _logger.debug('write params >>>>>: [%s.%s]' % (request.params.get('model'), request.params))
        # _logger.debug('write params method: [%s.%s]' % (request.params.get('model'), request.params.get('method')))
        if any(state != 'draft' for state in set(self.mapped('state')) if allow_write == False):
            raise UserError(_('Edit allowed only in draft state. [%s.%s]' % (
                request.params.get('model'), request.params.get('method'))))
        else:
            # _logger.info('Written vals: %s' % vals)
            return super().write(vals)