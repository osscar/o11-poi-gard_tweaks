# -*- coding: utf-8 -*-
# Copyright 2022 squid
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, _):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['purchase.order'].search[()]._compute_picking()
    env['purchase.order'].search[()]._get_landed_cost()

    # gender_mappings = {
    #     'female':
    #         env.ref('base.res_partner_title_madam') +
    #         env.ref('base.res_partner_title_miss'),
    #     'male': env.ref('base.res_partner_title_mister')
    # }
    # for gender, titles in list(gender_mappings.items()):
    #     env['res.partner'].with_context(active_test=False).search([
    #         ('title', 'in', titles.ids),
    #     ]).write({
    #         'gender': gender,
    #     })
