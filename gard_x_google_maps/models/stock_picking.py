# -*- encoding: utf-8 -*-
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)

# class ResPartnerArea(models.Model):
#     """ Inherit Drawing mixins model 'google_maps.drawing.shape.mixin' """
#     _name = 'res.partner.area'
#     _inherit = 'google_maps.drawing.shape.mixin'
#     _description = 'Partner Area'

#     partner_id = fields.Many2one(
#         'res.partner', required=True, ondelete='cascade')

# class ResPartnerTypeArea(models.Model):
#     """ Inherit Drawing mixins model 'google_maps.drawing.shape.mixin' """
#     _name = 'res.partner.type.area'
#     _inherit = 'google_maps.drawing.shape.mixin'
#     _description = 'Partner Type Area'

#     partner_type = fields.Many2one(
#         'res.partner.type', required=True, ondelete='cascade')


# class ResPartner(models.Model):
#     _inherit = 'res.partner'

#     shape_line_ids = fields.One2many(
#         'res.partner.area', 'partner_id', string='Area')

# class ResPartnerType(models.Model):
#     _inherit = 'res.partner.type'

#     shape_line_ids = fields.One2many(
#         'res.partner.type.area', 'partner_type', string='Area')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    partner_latitude = fields.Float(related="partner_id.partner_latitude")
    partner_longitude = fields.Float(related="partner_id.partner_longitude")
    date_localization = fields.Date(related="partner_id.date_localization")

    partner_street = fields.Char(related="partner_id.street")
    # partner_street2 = fields.Char()
    partner_city = fields.Char(related="partner_id.city")
    partner_state_id = fields.Many2one(related="partner_id.state_id")
    partner_country_id = fields.Many2one(related="partner_id.country_id")
    color = fields.Integer(related="picking_type_id.color")
    partner_image_small = fields.Binary(related="partner_id.image_small")

    # @api.multi
    # def _geo_localize(self):
    #     # We need country names in English below
    #     partners = [pk.partner_id.id for pk in self]
    #     partners = self.env['res.partner'].search([('id','in',partners)])
    #     return partners.geo_localize()
