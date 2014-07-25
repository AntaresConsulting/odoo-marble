# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _

from operator import itemgetter

import logging
_logger = logging.getLogger(__name__)

# import pdb
# pdb.set_trace()

class product_category(osv.osv):

    _inherit = 'product.category'
    _name = 'product.category'

    _columns = {

    }

#    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
#        res = super(product_category, self).name_get(cr, uid, ids, context=context)
#
#        _logger.info(">> _name_get_fnc >> 11 >> res = %s", res)
#        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=10):
        ids = []

        ids = self.search(cr, uid, ids, context=context)
        # _logger.info(">> name_search >> 22 >> iids = %s", ids)

        res = self.name_get(cr, uid, ids, context=context)
        # _logger.info(">> name_search >> 23 >> res = %s", res)

        res = sorted(res, key=itemgetter(1))
        # _logger.info(">> name_search >> 24 >> res = %s", res)

        return res

product_category()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
