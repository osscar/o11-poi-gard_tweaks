# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _open_route_map(self):
        partners = [pk.partner_id.id for pk in self]
        partners = self.env['res.partner'].search([('id','in',partners)])
        _logger.debug('orm len(partners) >>> %s', len(partners))
        if len(self) > 1:
            return partners.open_route_map()
        else:
            return partners[0].open_route_map()
        