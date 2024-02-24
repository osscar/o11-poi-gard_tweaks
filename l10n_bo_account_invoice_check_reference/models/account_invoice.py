# -*- coding: utf-8 -*-
##############################################################################
#
#    Bli Bli, Ltd.
#    Copyleft and swindle theft.
#    Author: squid
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from odoo import fields, models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    # @api.multi
    def _get_warning_msg(self):
        warning = False
        if not self._context.get("type_warn") == "cc_dup":
            pass
        warning = {
                "warning": {
                    "title": _("Duplicate Reference"),
                    "message": _(
                        "Please verify duplicate references."
                    )
                },
            }
        return warning
            
    @api.onchange("reference", "cc_nro_purch", "cc_aut", "rendition_ids")
    def onchange_reference(self):
        search_duplicate = False
        warning = False
        cc_check = (self.cc_nro_purch and self.cc_aut) != False
        if cc_check:
            search_duplicate = self.search([('company_id', '=', self.company_id.id), ('commercial_partner_id', '=', self.commercial_partner_id.id), ('id', '!=', self._origin.id), '&', ('cc_nro_purch', '=', self.cc_nro_purch), ('cc_aut', '=', self.cc_aut)]).filtered(lambda ri: ri.estado_fac == 'V')
        if search_duplicate:
            if self._context.get("type_check") == "cc_dup":
                warning = True
            else:
                warning = self.with_context(type_warn="cc_dup")._get_warning_msg()
        return warning

    # @api.multi
    def _check_duplicate_supplier_reference(self):
        res = super()._check_duplicate_supplier_reference()
        # check fiscal l10n_bo warnings
        if not self.with_context(type_check="cc_dup").onchange_reference():
            pass
        return res