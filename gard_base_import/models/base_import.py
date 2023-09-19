# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

from odoo import models, fields, api

class CustomImportWizard(models.TransientModel):
    _inherit = 'base_import.import'

    # Override the fields to remove unnecessary options
    model_id = fields.Many2one(domain="[('model', '=', 'base_import.export')]", string="Export List", required=True)

    # Override the method to check security group access
    @api.onchange('model_id')
    def _onchange_model_id(self):
        if self.model_id:
            user = self.env.user
            allowed_groups = self.env.ref('your_module.group_export_list_users')
            if user and allowed_groups and allowed_groups in user.groups_id:
                # User is in the allowed security group
                return
            else:
                # User does not have access to this export list
                self.model_id = False

    def do(self, fields):
        # Perform import action here
        super(CustomImportWizard, self).do(fields)

from odoo import models, fields

class BaseImportExport(models.Model):
    _inherit = 'base_import.export'

    security_group_id = fields.Many2one('res.groups', string="Security Group")
