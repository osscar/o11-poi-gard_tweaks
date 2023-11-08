# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class MapWebsite(models.Model):
    _inherit = 'map.website'

    multi_route_url = fields.Char(
        string='Multi Route URL',
        help="In this URL, {GEOCOORDS} will be "
        "replaced by the partner addresses or coordinates.")
