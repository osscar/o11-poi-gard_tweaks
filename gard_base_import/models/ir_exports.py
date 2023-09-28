# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

from odoo import models, fields

class IrExports(models.Model):
    _inherit = 'ir.exports'

    is_user_template = fields.Boolean(string='User Template')
