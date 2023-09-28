from odoo import http
from odoo.http import request

class ImportModelDataController(http.Controller):

    @http.route('/gard_base_import', type='http', auth="user")
    def import_model_data_redirect(self, **kwargs):
        _logger.debug("imdr type >>>: %s", type)
        _logger.debug("imdr auth >>>: %s", auth)
        # Check if the user belongs to your modulany import groups
        res = super(ImportModelDataController, self).import_model_data_redirect(**kwargs)
        
        user = request.env.user
        group_base_import = ["gard_base_import.group_base_import"]
        groups_user = group_base_import
        request_groups = (request.env.ref(gr) for gr in groups_user)
        if request_groups in user.groups_id:
            _logger.debug("imdr auth >>>: %s", auth)
            # User doesn't belong to any import groups, allow native behavior
            pass
        groups_redirect = ['gard_base_import.group_user', 'gard_base_import.group_manager']
        groups_user = groups_redirect
        groups_user = (request.env.ref(gr) for gr in groups_user)
        if request_groups in user.groups_id:
            # User belongs to any import groups, capture context and redirect to custom import
            context = request.env.context
            res = request.redirect('/web#action=action_open_import_wizard' + '&context=' + context)

        return res
