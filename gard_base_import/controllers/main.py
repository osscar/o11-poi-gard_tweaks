from odoo import http
from odoo.http import request

class ImportModelDataController(http.Controller):

    @http.route('/gard_base_import', type='http', auth="user")
    def import_model_data_redirect(self, **kwargs):
        # Check if the user belongs to your module's non-admin group
        user = request.env.user
        groups_redirect = ['gard_base_import.group_user', 'gard_base_import.group_manager']
        groups_user = (request.env.ref(rg) for rg in groups_redirect)  # Replace with your non-admin group XML ID

        if groups_user in user.groups_id:
            # User belongs to the non-admin group, capture context and redirect to custom import
            context = request.env.context
            return request.redirect('/web#action=action_open_import_wizard' + '&context=' + context)

        # User doesn't belong to the non-admin group, allow native behavior
        return super(ImportModelDataController, self).import_model_data_redirect(**kwargs)
