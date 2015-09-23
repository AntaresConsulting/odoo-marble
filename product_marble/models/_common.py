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

from openerp import api
from openerp.osv import osv
from openerp.osv import fields
import logging
_logger = logging.getLogger(__name__)

# import pdb; pdb.set_trace()
# import vimpdb; vimpdb.hookPdb()

# set propertie global...
RAW         = 'raw'
BACHA       = 'bacha'
SERVICE     = 'service'
INPUT       = 'input'
OTHER       = '*'

M2          = 'm2'
AREA        = 'area'
UNITS       = 'units'

LOC_DESPACHO    = 'loc_despacho'
LOC_STOCK       = 'stock'
LOC_REC_STOCK   = 'rec_stock'
LOC_OWN_STOCK   = 'own'
LOC_CUSTOMERS   = 'customers'

MAIN_COMPANY    = 'company'

_xml_data   = {
    # ---- Prod Categ -----
    RAW    : 'product_marble.prod_categ_raw_material',
    BACHA  : 'product_marble.prod_categ_bachas',
    SERVICE: 'product_marble.prod_categ_services',
    INPUT  : 'product_marble.prod_categ_inputs',
    # ---- Prod UOM -----
    M2      : 'product_marble.product_uom_square_meter',
    AREA    : 'product_marble.product_uom_categ_area',
    UNITS   : 'product.product_uom_categ_unit',
    # ---- Warehouse location Stock -----
    LOC_DESPACHO    : 'product_marble.location_deposito_despacho',
    LOC_STOCK       : 'product_marble.location_deposito_stock_propio',
    LOC_OWN_STOCK   : 'product_marble.location_deposito_stock_propio',
    LOC_CUSTOMERS   : 'product_marble.location_deposito_stock_clientes',
    LOC_REC_STOCK   : 'product_marble.location_deposito_stock_propio_recortes',
    # ---- Base Company -----
    MAIN_COMPANY   : 'base.main_company',
}
_prop   = {}

@api.model
def set_prop(self):
    global _prop
    for key in _xml_data:
        xml_id = _xml_data[key]
        if not _prop.get(key) or _prop.get(key) < 0:
            ids = self.env.ref(xml_id)
            _prop[key] = ids.id if ids and ids.id > 0 else -1
    #_logger.info(">> set_prop >> _prop = %s", _prop)

@api.model
def get_prod_types(self):
    #_logger.info(">> get_prod_type >> 1- self = %s", self)
    types = {
        get_prop(self, RAW)     : RAW,
        get_prop(self, BACHA)   : BACHA,
        get_prop(self, SERVICE) : SERVICE,
        get_prop(self, INPUT)   : INPUT,
    }
    #_logger.info(">> get_prod_type >> 2- types = %s", types)
    return types

# --- Migracion -------------------------
#
# def get_prop(self, cr, uid, key):
#     global _prop
#     if not _prop.get(key):
#         set_prop(self, cr, uid, [])
#     return _prop[key]

@api.model
def get_prop(self, key):
    global _prop
    # valido db...
    db = 'db_name'
    db_name = _prop.get(db,False)
    if (not db_name or db_name != self._cr.dbname):
        _prop.clear()
        _prop[db] = self._cr.dbname
    #
    if not _prop.get(key):
        set_prop(self)

    return _prop[key]
# ----------------------------------------

# --- Migracion -------------------------
#
# def get_raw_material_id(self, cr, uid):
#    return get_prop(self, cr, uid, 'raw_material_id')
#
# def get_bachas_id(self, cr, uid):
#    return get_prop(self, cr, uid, 'bachas_id')
#
# def get_services_id(self, cr, uid):
#     return get_prop(self, cr, uid, 'services_id')
#
# def get_inputs_id(self, cr, uid):
#     return get_prop(self, cr, uid, 'inputs_id')
#
# def get_uom_m2_id(self, cr, uid):
#     return get_prop(self, cr, uid, 'uom_m2_id')
#
# def get_uom_units_id(self, cr, uid):
#     return get_prop(self, cr, uid, 'uom_units_id')

@api.model
def get_raw_material_id(self):
    return get_prop(self, RAW)

@api.model
def get_bachas_id(self):
    return get_prop(self, BACHA)

@api.model
def get_services_id(self):
    return get_prop(self, SERVICE)

@api.model
def get_inputs_id(self):
    return get_prop(self, INPUT)

@api.model
def get_uom_m2_id(self):
    return get_prop(self, M2)

@api.model
def get_uom_units_id(self):
    return get_prop(self, UNITS)

@api.model
def get_location_despacho(self):
    return get_prop(self, LOC_DESPACHO)

@api.model
def get_location_stock(self):
    return get_prop(self, LOC_STOCK)

@api.model
def get_location_recortes_stock(self):
    return get_prop(self, LOC_REC_STOCK)


@api.model
def get_location_own_id(self):
    return get_prop(self, LOC_OWN_STOCK)

@api.model
def get_location_customers_id(self):
    return get_prop(self, LOC_CUSTOMERS)

@api.model
def get_main_company_id(self):
    return get_prop(self, MAIN_COMPANY)
# ----------------------------------------

# --- Migracion -------------------------
#
# def is_raw_material(self, cr, uid, cid):
#     return (cid == get_prop(self, cr, uid, RAW))
#
# def is_bachas(self, cr, uid, cid):
#     return (cid == get_prop(self, cr, uid, BACHAS))
#
# def is_services(self, cr, uid, cid):
#     return (cid == get_prop(self, cr, uid, SERVICES))
#
# def is_inputs(self, cr, uid, cid):
#     return (cid == get_prop(self, cr, uid, INPUTS))

@api.model
def is_raw_material(self, cid):
    return (cid == get_prop(self, RAW))

@api.model
def is_bachas(self, cid):
    return (cid == get_prop(self, BACHA))

@api.model
def is_services(self, cid):
    return (cid == get_prop(self, SERVICE))

@api.model
def is_inputs(self, cid):
    return (cid == get_prop(self, INPUT))
# ----------------------------------------

# def get_raw_material_id(self, cr, uid):
#    # ids = self.pool.get('product.category').search(cr, uid, [('name','ilike','Marble Work')], limit=1)
#    # return ids[0] or False
#    return get_raw_material_id(self, cr, uid)

# def get_product_uom_m2_id(self, cr, uid):
#     global _prop
#    key = 'uom_m2_id'
#
#    if (not _prop) or (_prop.get(key) < 0):
#        obj = self.pool.get('product.uom')
#        ids = obj.search(cr, uid, [('name','ilike','m2')], limit=1)
#        _prop[key] = ids[0] if ids and ids[0] > 0 else -1
#
#    # _logger.info("3 >> get_product_uom_m2_id >> _prop = %s", _prop)
#    return _prop[key]

def is_raw_material_by_category_id(self, cr, uid, ids):
    """
        - Obj:  Determina si Category [ids] es Marble Work
                si  pertenece a la categ: Marble Work o no...
        - Inp:  [ids] = lista de category_id.
        - Out:  {category_id: true/false, ..}
    """
    result = {}
    if not ids:
        return result

    marble_work_id = get_raw_material_id(self, cr, uid)
    result = {c:(c == marble_work_id) for c in ids}

    # _logger.info("1 >> is_raw_material_by_category_id >> result = %s", result)
    return result


def is_raw_material_by_product_id(self, cr, uid, ids):
    """
        - Obj:  Determina por cada producto [ids],
                si  pertenece a la categ: Marble Work o no...
        - Inp:  [ids] = lista de products ids.
        - Out:  {prod_id: is_marble, ..}
    """
    result = {}
    if not ids:
        return result

    marble_work_id = get_raw_material_id(self, cr, uid)
    obj = self.pool.get('product.product')
    for p in obj.read(cr, uid, ids, ['categ_id']):
        result.update({p['id']: (marble_work_id == p['categ_id'][0])})

#    _logger.info("1 >> is_raw_material_by_product_id >> result = %s", result)

    return result

def is_bacha_by_product_id(self, cr, uid, ids):
    result = {}
    if not ids:
        return result

    bacha_id = get_bachas_id(self, cr, uid)
    obj = self.pool.get('product.product')

    for p in obj.read(cr, uid, ids, ['categ_id']):
        result.update({p['id']: (bacha_id == p['categ_id'][0])})

    # _logger.info("1 >> is_raw_material_by_product_id >> result = %s", result)
    return result

def is_input_by_product_id(self, cr, uid, ids):
    result = {}
    if not ids:
        return result

    input_id = get_inputs_id(self, cr, uid)
    obj = self.pool.get('product.product')

    for p in obj.read(cr, uid, ids, ['categ_id']):
        result.update({p['id']: (input_id == p['categ_id'][0])})

    # _logger.info("1 >> is_raw_material_by_product_id >> result = %s", result)
    return result


def is_service_by_product_id(self, cr, uid, ids):
    result = {}
    if not ids:
        return result

    service_id = get_services_id(self, cr, uid)
    obj = self.pool.get('product.product')

    for p in obj.read(cr, uid, ids, ['categ_id']):
        result.update({p['id']: (service_id == p['categ_id'][0])})

    # _logger.info("1 >> is_raw_material_by_product_id >> result = %s", result)
    return result



# def get_data(self, cr, uid, list_tuple, fid):
#    """
#        - Obj:  Recupero 'value' segun 'fid' (find id), en list_tuple...
#        - Inp:
#            arg 4: [list_tuple] = lista de tuplas: [(id, value to display), ..]
#            arg 5: [fid] = 'fid' a localizar en 'list_tuple'.
#        - Out:  'value' referenciado por 'fid'.
#    """
#    if not list_tuple or not fid:
#        return ""
#
#    return dict(list_tuple).get(fid)


# ---------- Stock ----------

def query_stock_move_input(self, cr, uid):
    str = "\n\n >>> Stock Move Input <<<\n"
    obj = self.pool.get('stock.move')

    domain = [
        '&','|',

        '&',
        ('picking_id','=',False),
        ('location_id.usage', 'in', ['customer','supplier']),

        '&',
        ('picking_id','!=',False),
        ('picking_id.type','=','in'),

        ('plaque_id','>','0')
    ]

    ids = obj.search(cr, uid, domain)
    _logger.info(">> query_stock_input >> 1 >> ids = %s", ids)

    for m in obj.browse(cr, uid, ids):
        str += "%s - %s - %s - %s - %s \n" % (m.id, m.product_uom, m.plaque_id, m.plaque_qty, m.name)

    _logger.info(str)
    return True

def query_stock_move_output(self, cr, uid):
    str = "\n\n >>> Stock Move Output <<<\n"
    obj = self.pool.get('stock.move')

    domain = [
        '&','|',

        '&',
        ('picking_id','=',False),
        ('location_dest_id.usage', 'in', ['customer','supplier']),

        '&',
        ('picking_id','!=',False),
        ('picking_id.type','=','out'),

        ('plaque_id','>','0')
    ]

    ids = obj.search(cr, uid, domain)
    _logger.info(">> query_stock_input >> 2 >> ids = %s", ids)

    for m in obj.browse(cr, uid, ids):
        str += "%s - %s - %s - %s - %s \n" % (m.id, m.product_uom, m.plaque_id, m.plaque_qty, m.name)

    _logger.info(str)
    return True


def get_stock_move_by_product(self, cr, uid, ids):
    _logger.info(">> get_stock_move_by_product >> 000 >> ids = %s", ids)

    str = "\n\n >>> Stock Move In/Out by Product <<<\n"
    obj = self.pool.get('stock.move')

    domain = [
        # ('product_id.categ_id','=', get_raw_material_id(self, cr, uid)), << producto tipo marble.
        ('product_id', 'in', ids),
    ]
    _logger.info(">> get_stock_move_by_product >> 111 >> domain = %s", domain)

    ids = obj.search(cr, uid, domain)
    _logger.info(">> get_stock_move_by_product >> 222 >> ids = %s", ids)

    for m in obj.browse(cr, uid, ids):
        str += "%s - %s - %s - %s - %s \n" % (m.id, m.product_uom, m.plaque_id, m.plaque_qty, m.name)

    _logger.info(str)
    return True


def query_stock_move_test(self, cr, uid):
    query_stock_move_input(self, cr, uid)
    query_stock_move_output(self, cr, uid)

# -------------------------------------------------------
def print_dict(msg, val):
    nl = '\n'
    res = msg + nl + nl
    for k in val:
        res += str(k) + ':' + str(val[k]) + nl

    res += nl + nl
    _logger.info(res)


# -------------------------------------------------------

def get_loc_parents(self, loc, res):
    res += (loc and loc.id and [loc.id]) or []
    if loc and loc.location_id:
        get_loc_parents(self, loc.location_id, res)
    return res








# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
