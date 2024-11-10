# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models
from odoo import SUPERUSER_ID, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class MergePartnerAutomatic(models.TransientModel):
    """
        The idea behind this wizard is to create a list of potential partners to
        merge. We use two objects, the first one is the wizard for the end-user.
        And the second will contain the partner list to merge.
    """

    _inherit = 'base.partner.merge.automatic.wizard'

    def _merge(self, partner_ids, dst_partner=None):
        """ private implementation of merge partner
            :param partner_ids : ids of partner to merge
            :param dst_partner : record of destination res.partner
        """
        
        if self.env.user.has_group('base_partner_merge_security_group.group_partner_merge_manager'):
            Partner = self.env['res.partner']
            partner_ids = Partner.browse(partner_ids).exists()
            if len(partner_ids) < 2:
                return

            if len(partner_ids) > 3:
                raise UserError(_("For safety reasons, you cannot merge more than 3 contacts together. You can re-open the wizard several times if needed."))

            # check if the list of partners to merge contains child/parent relation
            child_ids = self.env['res.partner']
            for partner_id in partner_ids:
                child_ids |= Partner.search([('id', 'child_of', [partner_id.id])]) - partner_id
            if partner_ids & child_ids:
                raise UserError(_("You cannot merge a contact with one of his parent."))

            # remove dst_partner from partners to merge
            if dst_partner and dst_partner in partner_ids:
                src_partners = partner_ids - dst_partner
            else:
                ordered_partners = self._get_ordered_partner(partner_ids.ids)
                dst_partner = ordered_partners[-1]
                src_partners = ordered_partners[:-1]
            _logger.info("dst_partner: %s", dst_partner.id)

            # call sub methods to do the merge
            self._update_foreign_keys(src_partners, dst_partner)
            self._update_reference_fields(src_partners, dst_partner)
            self._update_values(src_partners, dst_partner)

            _logger.info('(uid = %s) merged the partners %r with %s', self._uid, src_partners.ids, dst_partner.id)
            dst_partner.message_post(body='%s %s' % (_("Merged with the following partners:"), ", ".join('%s <%s> (ID %s)' % (p.name, p.email or 'n/a', p.id) for p in src_partners)))

            # delete source partner, since they are merged
            src_partners.unlink()
        else:
            super()._merge(partner_ids, dst_partner=None)