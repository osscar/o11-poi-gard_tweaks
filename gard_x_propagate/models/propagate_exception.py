# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PropagateException(models.Model):
    _name = "propagate.exception"

    def _get_exc_expr(self, params):
        # get state field related expressions
        res = {}

        if params["field"] == "state":
            res["field_vals"] = [rs for s in params["field_vals"] for rs in self.env[params["model"]]._fields(params["field"]).selection if rs[0] == s]
        
        return res


    def _exception_check(self, params):
        # check exceptions
        exc_vals = params["exc_vals"]

        # state field exceptions
        if exc_vals["field"] == "state":
            exc_vals["is_exc"] = exc_vals["field_rec_vals"] not in tuple(es for es in exc_vals["field_vals"])
        
        # compose exception message
        exc_msg = exc_vals["msg"]
        if exc_vals["is_exc"]:
            # get exception expressions to build validation message
            exc_exp = self._get_exc_expr(exc_vals)["field_vals"]
            exc_vals["msg"] += str(exp[1] for exp in exc_exp + ", ") + "."
            raise ValidationError(("%s") % exc_msg)

        return True
