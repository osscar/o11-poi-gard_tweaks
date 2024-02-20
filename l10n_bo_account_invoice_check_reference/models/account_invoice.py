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

    @api.onchange("reference", "cc_nro_purch", "cc_aut", "rendition_ids")
    def onchange_reference(self):
        _logger.debug("onch_ref self, self.id >>>: %s: %s", self, self._origin.id)
        self = self.browse(self._origin.id)
        _logger.debug("onch_ref self, self.id >>>: %s: %s", self, self.ids)
        search_duplicate = []
        for invoice in self:
            _logger.debug("onch_ref invoice, invoice.id >>>: %s: %s", invoice, invoice.id)
            cc_check = (invoice.cc_nro_purch and invoice.cc_aut) != False
            _logger.debug("onch_ref cc_check >>>: %s", cc_check)
            if cc_check:
                search_duplicate = invoice.search([('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id), '&', ('cc_nro_purch', '=', invoice.cc_nro_purch), ('cc_aut', '=', invoice.cc_aut)])
                # _logger.debug("onch_ref cc_check, cc_search_duplicate >>>: %s: %s", cc_check, search_duplicate)
        if search_duplicate:
            return {
                        "warning": {
                            "title": _("Duplicate Reference"),
                            "message": _(
                                "Please verify duplicate references. %s"
                            ) % (["Ref. - Aut. " + str(sd.cc_nro_purch + " " + sd.cc_aut) for sd in search_duplicate]),
                        },
                    }

    # @api.multi   
    # def _check_duplicate_supplier_reference(self):
    #     res = super()._check_duplicate_supplier_reference()
    #     _logger.debug("_cdsr >>>: %s", self)
    #     for invoice in self:
    #         # refuse to validate a vendor bill/credit note if there already exists one with the same reference for the same partner,
    #         # because it's probably a double encoding of the same bill/credit note
    #         if invoice.type in ('in_invoice', 'in_refund') and invoice.reference and invoice.cc_nro_purch:
    #             _logger.debug("_cdsr if invoice.cc_nro_purch >>>: %s", invoice.cc_nro_purch)
    #             if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), '&amp;', ('cc_nro_purch', '=', invoice.cc_nro_purch), ('cc_aut', '=', invoice.cc_aut), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id)]):
    #                 raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/credit note. %s: %s", invoice.cc_nro_purch, invoice.cc_aut))
    #             else:continue
    #     return res