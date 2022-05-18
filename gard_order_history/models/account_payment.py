# -*- coding: utf-8 -*-

# import logging

from odoo import models, fields, api, exceptions, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    journal_type = fields.Selection(related='journal_id.type', string='Journal Type', readonly=True)
    journal_code = fields.Char(related='journal_id.code', string='Journal Type', readonly=True)
