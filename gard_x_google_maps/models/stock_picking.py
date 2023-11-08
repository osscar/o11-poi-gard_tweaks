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

    @classmethod
    def _geo_localize(cls, apikey, street="", zip="", city="", state="", country=""):
        search = geo_query_address(
            street=street, zip=zip, city=city, state=state, country=country
        )
        result = geo_find(search, apikey)
        if result is None:
            search = geo_query_address(city=city, state=state, country=country)
            result = geo_find(search, apikey)
        return result

    @api.multi
    def geo_localize(self):
        # We need country names in English below
        apikey = (
            self.env["ir.config_parameter"].sudo().get_param("google.api_key_geocode")
        )
        for partner in self.partner_id.with_context(lang="en_US"):
            result = partner._geo_localize(
                apikey,
                partner.street,
                partner.zip,
                partner.city,
                partner.state_id.name,
                partner.country_id.name,
            )
            if result:
                partner.write(
                    {
                        "partner_latitude": result[0],
                        "partner_longitude": result[1],
                        "date_localization": fields.Date.context_today(partner),
                    }
                )
        return True
