# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# from ast import literal_eval
# import functools
# import itertools
import logging
# import psycopg2

from odoo import models
# from odoo import models, _
from odoo import SUPERUSER_ID, _
# from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import UserError
# from odoo.tools import mute_logger

# _logger = logging.getLogger("base.partner.merge")
_logger = logging.getLogger(__name__)

class MergePartnerAutomatic(models.TransientModel):

    _inherit = "base.partner.merge.automatic.wizard"
    # _order = "min_id asc"

    def _merge(self, partner_ids, dst_partner=None):
        # _logger.debug('_merge is crm manager >>>: %s', self.env.user.has_group('base_partner_merge_security_group.group_partner_merge_manager'))
        # if not self.pool.get('res.users').has_group(cr, uid, 'crm_merge_security_group.group_crm_merge_manager'):
        # res = super()._merge(partner_ids, dst_partner=None)
        _logger.debug('_merge SUPERUSER_ID >>>: %s', SUPERUSER_ID)
        # _logger.debug('_merge SUPERUSER_ID global post >>>: %s', SUPERUSER_ID)
        super_user = SUPERUSER_ID
        # if super_user != self.env.uid:
        if self.env.user.has_group('base_partner_merge_security_group.group_partner_merge_manager'):
            _logger.debug('_merge bpm manager >>>: %s', self.env.user.has_group('base_partner_merge_security_group.group_partner_merge_manager'))
            SUPERUSER_ID = self.env.uid
        # return res
        super()._merge(partner_ids, dst_partner=None)
        # SUPERUSER_ID = super_user
        
        #     """private implementation of merge partner
        #     :param partner_ids : ids of partner to merge
        #     :param dst_partner : record of destination res.partner
        #     """
        #     Partner = self.env["res.partner"]
        #     partner_ids = Partner.browse(partner_ids).exists()
        #     if len(partner_ids) < 2:
        #         return

        #     if len(partner_ids) > 3:
        #         raise UserError(
        #             _(
        #                 "For safety reasons, you cannot merge more than 3 contacts together. You can re-open the wizard several times if needed."
        #             )
        #         )

        #     # check if the list of partners to merge contains child/parent relation
        #     child_ids = self.env["res.partner"]
        #     for partner_id in partner_ids:
        #         child_ids |= (
        #             Partner.search([("id", "child_of", [partner_id.id])]) - partner_id
        #         )
        #     if partner_ids & child_ids:
        #         raise UserError(_("You cannot merge a contact with one of his parent."))

        #     # check only admin can merge partners with different emails
        #     # if (
        #     #     SUPERUSER_ID != self.env.uid
        #     #     and len(set(partner.email for partner in partner_ids)) > 1
        #     # ):
        #     #     raise UserError(
        #     #         _(
        #     #             "All contacts must have the same email. Only the Administrator can merge contacts with different emails."
        #     #         )
        #     #     )

        #     # remove dst_partner from partners to merge
        #     if dst_partner and dst_partner in partner_ids:
        #         src_partners = partner_ids - dst_partner
        #     else:
        #         ordered_partners = self._get_ordered_partner(partner_ids.ids)
        #         dst_partner = ordered_partners[-1]
        #         src_partners = ordered_partners[:-1]
        #     _logger.info("dst_partner: %s", dst_partner.id)

        #     # # FIXME: is it still required to make and exception for account.move.line since accounting v9.0 ?
        #     # if (
        #     #     SUPERUSER_ID != self.env.uid
        #     #     and "account.move.line" in self.env
        #     #     and self.env["account.move.line"]
        #     #     .sudo()
        #     #     .search([("partner_id", "in", [partner.id for partner in src_partners])])
        #     # ):
        #     #     raise UserError(
        #     #         _(
        #     #             "Only the destination contact may be linked to existing Journal Items. Please ask the Administrator if you need to merge several contacts linked to existing Journal Items."
        #     #         )
        #     #     )

        #     # call sub methods to do the merge
        #     self._update_foreign_keys(src_partners, dst_partner)
        #     self._update_reference_fields(src_partners, dst_partner)
        #     self._update_values(src_partners, dst_partner)

        #     _logger.info(
        #         "(uid = %s) merged the partners %r with %s",
        #         self._uid,
        #         src_partners.ids,
        #         dst_partner.id,
        #     )
        #     dst_partner.message_post(
        #         body="%s %s"
        #         % (
        #             _("Merged with the following partners:"),
        #             ", ".join(
        #                 "%s <%s> (ID %s)" % (p.name, p.email or "n/a", p.id)
        #                 for p in src_partners
        #             ),
        #         )
        #     )

        #     # delete source partner, since they are merged
        #     src_partners.unlink()
            
        # else:
        #     super()._merge(partner_ids, dst_partner=None)