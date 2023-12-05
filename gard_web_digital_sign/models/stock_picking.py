# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Users(models.Model):
    _inherit = 'stock.picking'

    digital_signature = fields.Binary(string='Signature')
    signature_clarify = fields.Char(string='Clarification')
