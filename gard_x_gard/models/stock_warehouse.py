# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

<<<<<<< Updated upstream
from odoo import api, fields, models, _
# from odoo.exceptions import RedirectWarning, UserError, ValidationError
# from odoo.http import request

# import odoo.addons.decimal_precision as dp
=======
from odoo import fields, models, _
>>>>>>> Stashed changes

# _logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    code = fields.Char('Short Name', required=True, size=10, help="Short name used to identify your warehouse")
