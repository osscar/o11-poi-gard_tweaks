# -*- encoding: utf-8 -*-
from odoo import fields, models


class ResPartnerArea(models.Model):
    """ Inherit Drawing mixins model 'google_maps.drawing.shape.mixin' """
    _name = 'res.partner.area'
    _inherit = 'google_maps.drawing.shape.mixin'
    _description = 'Partner Area'

    partner_id = fields.Many2one(
        'res.partner', required=True, ondelete='cascade')

class ResPartnerTypeArea(models.Model):
    """ Inherit Drawing mixins model 'google_maps.drawing.shape.mixin' """
    _name = 'res.partner.type.area'
    _inherit = 'google_maps.drawing.shape.mixin'
    _description = 'Partner Type Area'

    partner_type = fields.Many2one(
        'res.partner.type', required=True, ondelete='cascade')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shape_line_ids = fields.One2many(
        'res.partner.area', 'partner_id', string='Area')

class ResPartnerType(models.Model):
    _inherit = 'res.partner.type'

    shape_line_ids = fields.One2many(
        'res.partner.type.area', 'partner_type', string='Area')


