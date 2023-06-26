# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PropagateException(models.Model):
    _name = "propagate.exception"

    def _exception_check(self, params):
        # context parameters for conditional statement
        # check exception
        exc_field = params["exc_field"]
        if exc_field == "state":
            exc_states = [rs for s in exc_states for rs in params["exc_model"]._fields[params["exc_field"]].selection if rs[0] == s]
            params["exc_msg"] += str(es[1] for es in exc_states + ", ") + "."
        params["is_exc"] = self.state not in tuple(es for es in exc_states)
        
        exc_msg = params["exc_msg"]
        if params["is_exc"]:
            raise ValidationError(("%s") % exc_msg)

        return True
