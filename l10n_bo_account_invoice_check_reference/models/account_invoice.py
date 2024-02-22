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
        title = ""
        msg = ""
        warning = False
        if self._context.get("type_warn")[0] == "cc_dup":
            pass
            # invoice_dup = self._context.get("type_warn")[1]
            # if invoice_dup:
            #     _logger.debug("onch_ref if warning >>>: %s", warning)
            #     for invoice in invoice_dup:
            #         ref = str(invoice.number)
            #         _logger.debug("onch_ref for ref >>>: %s", ref)
            #         # msg = {k:v for k,v in enumerate(msg)}
            # ref = ""
        
        # _logger.debug("onch_ref ref >>>: %s", ref)
        _logger.debug("onch_ref msg >>>: %s", msg)
        _logger.debug("onch_ref title >>>: %s", title)
        warning = {
                    "warning": {
                        "title": title,
                        "message": msg,
                    },
            }
        warning["warning"]["title"] = "title"
        # msg = "Please verify duplicate references: "
        # _logger.debug("onch_ref if warning post >>>: %s", warning)
        return warning
            
    @api.onchange("reference", "cc_nro_purch", "cc_aut", "rendition_ids")
    def onchange_reference(self):
        _logger.debug("onch_ref self, self.id >>>: %s: %s", self, self._origin.id)
        _logger.debug("onch_ref self, self._context >>>: %s: %s", self, self._context)
        search_duplicate = False
        warning = False
        cc_check = (self.cc_nro_purch and self.cc_aut) != False
        _logger.debug("onch_ref reference >>>: %s", self.reference)
        _logger.debug("onch_ref cc_nro_purch >>>: %s", self.cc_nro_purch)
        _logger.debug("onch_ref cc_aut >>>: %s", self.cc_aut)
        if cc_check:
            search_duplicate = self.search([('company_id', '=', self.company_id.id), ('commercial_partner_id', '=', self.commercial_partner_id.id), ('id', '!=', self._origin.id), '&', ('cc_nro_purch', '=', self.cc_nro_purch), ('cc_aut', '=', self.cc_aut)]).filtered(lambda ri: ri.estado_fac == 'V')
            _logger.debug("onch_ref cc_check, cc_search_duplicate >>>: %s: %s", cc_check, search_duplicate)
        if search_duplicate:
            if self._context.get("type_check") == "cc_dup":
                warning = True
            else:
                warning = self.with_context(type_warn=["cc_dup", search_duplicate])._get_warning_msg()
                # with_context().
        return warning

    # @api.multi
    def _check_duplicate_supplier_reference(self):
        res = super()._check_duplicate_supplier_reference()
        _logger.debug("_cdsr >>>: %s", self)
        # for invoice in self:
        _logger.debug("_cdsr if invoice.cc_nro_purch >>>: %s", invoice.cc_nro_purch)
        # check fiscal l10n_bo warnings
        if not self.with_context(type_check="cc_dup").onchange_reference():
            _logger.debug("_cdsr if invoice.cc_nro_purch >>>: %s", self)
            pass
        return res