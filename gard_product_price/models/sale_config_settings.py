# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

# _logger = logging.getLogger(__name__)


class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.multi
    def set_values(self):
        _logger.info("> Settings sign-up parameters")
        super(SaleConfiguration, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        ICPSudo.set_param('sale.sale_pricelist_setting', 'formula')
        # _logger.info("> ... done.")

    @api.model
    def get_values(self):
        res = super(SaleConfiguration, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        res.update({
            'sale_pricelist_setting': ICPSudo.get_param('sale.sale_pricelist_setting', default='formula'),
        })
        return res
