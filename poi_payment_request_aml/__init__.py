# -*- coding: utf-8 -*-
##############################################################################
#
#    Bli Bli, Ltd.
#    Copyleft and swindle theft.
#    Author: squid
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from . import models
from odoo import api, SUPERUSER_ID

def add_payment_request_links(cr, registry):
    """
    This hook will run automatically only after the module is installed.
    It will not run during module updates (-u).
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Call the method on the model. 
    # Since your method searches for all records internally, 
    # calling it on an empty recordset is sufficient.
    env['account.payment.request'].action_backfill_aml_links()