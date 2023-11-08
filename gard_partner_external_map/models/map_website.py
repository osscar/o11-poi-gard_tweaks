# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class MapWebsite(models.Model):
    _inherit = 'map.website'

    multi_route_address_url = fields.Char(
        string='Route URL that uses the addresses',
        help="In this URL, {GEOCOORDS} will be "
        "replaced by the start and destination addresses.")
    multi_route_lat_lon_url = fields.Char(
        string='Route URL that uses latitude and longitude',
        help="In this URL, {GEOCOORDS} will be replaced by the "
        "latitude and longitude of the start and destination adresses "
        "(requires the module 'base_geolocalize').")
