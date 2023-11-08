# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # @api.multi
    # def _address_as_string(self):
    #     self.ensure_one()
    #     addr = []
    #     if self.street:
    #         addr.append(self.street)
    #     if self.street2:
    #         addr.append(self.street2)
    #     if self.city:
    #         addr.append(self.city)
    #     if self.state_id:
    #         addr.append(self.state_id.name)
    #     if self.country_id:
    #         addr.append(self.country_id.name)
    #     if not addr:
    #         raise UserError(_("Address missing on partner '%s'.") % self.name)
    #     return ' '.join(addr)

    @api.multi
    def open_route_map(self):
        if len(self) < 2:
            return super().open_route_map()
        url = False
        geo_coords = {}
        route = False
        map_website = self.env.user.context_route_map_website_id
        _logger.debug('orm len(self) >>> %s', len(self))
        if len(self) > 1:
            if not self.env.user.context_route_map_website_id:
                raise UserError(
                    _('Missing route map website: '
                    'you should set it in your preferences.'))
            
            if not self.env.user.context_route_start_partner_id:
                raise UserError(
                    _('Missing start address for route map: '
                    'you should set it in your preferences.'))
            start_partner = self.env.user.context_route_start_partner_id
            if (start_partner.partner_latitude and start_partner.partner_longitude):
                geo_coords['{GEOCOORDS}'] = str(start_partner.partner_latitude) + ", " + str(start_partner.partner_longitude)
            else:
                geo_coords['{GEOCOORDS}'] = start_partner._address_as_string()
            _logger.debug('orm start_partner geo_coords >>> %s', geo_coords)
            for partner in self:
                if (map_website.multi_route_lat_lon_url and
                        hasattr(partner, 'partner_latitude') and
                        partner.partner_latitude and partner.partner_longitude):
                    route = "multi_route_lat_lon_url"
                    _logger.debug('orm mrllu geo_coords >>> %s', geo_coords)
                    geo_coords['{GEOCOORDS}'] += "/" + str(partner.partner_latitude)  + ", " + str(partner.partner_longitude)
                else:
                    if not map_website.multi_route_address_url:
                        raise UserError(
                            _("Missing route URL that uses the addresses "
                                "for the map website '%s'") % map_website.name)
                    route = "multi_route_address_url"
                    geo_coords['{GEOCOORDS}'] += "/" + partner._address_as_string()
                    _logger.debug('orm mrau geo_coords >>> %s', geo_coords)
            url = self.env['res.partner']._prepare_url(map_website[route], geo_coords)
            _logger.debug('orm url map_website[route] >>> %s', map_website[route])
            _logger.debug('orm url post >>> %s', url)
            _logger.debug('orm geo_coords post >>> %s', geo_coords)
                
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }