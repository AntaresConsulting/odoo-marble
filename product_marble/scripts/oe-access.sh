#!/usr/bin/env python
from __future__ import print_function
import erppeek
import sys, os
import psycopg2 

# constants -------------------------------------------------

CONFIG_FILE = 'db-00'
SERVER = 'localhost'
USER_DB = 'openerp'
PSW_DB = 'opener'

SIZE = [50,20,5,40,30,6,6,6,6]
FIELDS = ['model','level','id','xml_id','group','read','write','create','unlink']

# functions -------------------------------------------------

def _check_argum():
    model_filter = False
    group_filter = False
    model = ''
    group = ''

    # defino extend 
    extend = '-e' in sys.argv
    if extend:
        sys.argv.remove('-e')

    # defino module + group
    pos_m = 0; pos_g = 0
    size_arg = len(sys.argv)
    k = 1
    pos_m = size_arg > k and str(sys.argv[k]) == '-m' and k
    pos_g = size_arg > k and str(sys.argv[k]) == '-g' and k
    k = 3 
    pos_m = pos_m or (size_arg > k and str(sys.argv[k]) == '-m' and k)
    pos_g = pos_g or (size_arg > k and str(sys.argv[k]) == '-g' and k)

    mg = ['-m','-g']
    if pos_m:
        model = size_arg > pos_m+1 and str(sys.argv[pos_m+1])
        model = model not in mg and model
        model_filter = model and pos_m and True
    if pos_g:
        group = size_arg > pos_g+1 and str(sys.argv[pos_g+1])
        group = group not in mg and group
        group_filter = group and pos_g and True

    if not (model or group):
        print("""
        oe-access.sh [-m <model>] [-g <group-xml-id>] [-e]
        > -m <model>: filter by model, p/ex: -m product.marble.dimension
        > -g <group-xml-id>: filter by group, 'module.xml_id' p/ex: -g product_marble.group_marble_adminis
        > -e: extend result, when input only -m or -g the option -e describe full the result.

        > ex: oe-access.sh -g product_marble.group_marble_adminis  
        > ex: oe-access.sh -m product.marble.dimension
        > ex: oe-access.sh -g product_marble.group_marble_adminis -m product.marble.dimension
        """)
        sys.exit(0)

    model = model if model else ''
    group = group if group else ''

    # xxx = 'mod-f = %s, mod = %s, gru-f = %s, gru = %s'
    # print(xxx % (model_filter, model, group_filter, group))
    return extend, model, group 

def _exists_model(model_name):
    ids = pmodel.search([('model', '=', model_name)])
    return (len(ids) > 0)

def _get_level(lgroups, gid):
    for e in lgroups:
        if e[0] == gid:
            return e[1]
    return ''

# - - - - - - - - - - -  - - - -

def _get_sql(group_ids, model):
    group_ids = str(group_ids).lstrip('[').rstrip(']')

    groups_filter = " AND g.id IN (%s) " % group_ids if group_ids else ''
    models_filter = " AND m.model = '%s' " % model if model else ''

    sql = '''
        SELECT
            d.name, g.id, g.name, m.model, a.perm_read,
            a.perm_write, a.perm_create, a.perm_unlink
        FROM
            ir_model_access a
            JOIN ir_model m ON (a.model_id=m.id)
            JOIN res_groups g ON (a.group_id=g.id)
            LEFT JOIN ir_model_data d ON (d.model = 'res.groups' AND d.res_id=g.id)
        WHERE
              a.active IS True
         %s 
         %s 
        ORDER BY m.model, g.name;
        ''' % (groups_filter, models_filter) 

    #print('4- sql = %s' % sql)
    return sql

def _mapping(cur, lgroups):
    res = []

    # 1. recupero los grupos hallados para un model especifico.
    # FIELDS = ['model','level','id','xml_id','group','read','write','create','unlink']
    val = [{FIELDS[0]:c[3],
            FIELDS[1]:_get_level(lgroups, c[1]),
            FIELDS[2]:c[1],
            FIELDS[3]:lref[c[1]][0],
            FIELDS[4]:c[2],
            FIELDS[5]:c[4],
            FIELDS[6]:c[5],
            FIELDS[7]:c[6],
            FIELDS[8]:c[7]
        } for c in cur]
    #print('1- val = %s' % val)
    
    # 2. completo los grupos faltantes del model especifico.
    # lgro =  [(58, '58'), (14, '58>14'), (13, '58>14>13'), (5, '58>14>13>5'), (21, '58>14>13>5>21')]
    for gid, level in [gro for gro in lgroups]:
        #print('2- gid = %s, level = %s' % (gid, level))
        
        # val > [{'col1':'val1',..},{'col1':'val1',..},..]
        data = [v for v in val if v['id'] == gid]
        #print('3- data = %s' % data)

        # FIELDS = ['model','level','id','xml_id','group','read','write','create','unlink']
        if not data:
            data = [{FIELDS[0]:'',
                     FIELDS[1]:level,
                     FIELDS[2]:str(gid),
                     FIELDS[3]:lref[gid][0],
                     FIELDS[4]:lref[gid][1],
                     FIELDS[5]:'',
                     FIELDS[6]:'',
                     FIELDS[7]:'',
                     FIELDS[8]:''
                   }]
            #print('4- data = %s' % data)
        res += data

    # val > [{'col1':'val1',..},{'col1':'val1',..},..]
    return res 

def _process_model_groups(lmodels):
    ldata = []
    for mod, lgroups in lmodels:
        #print('20- model = %s' % mod)
        #print('21- lgroups = %s' % lgroups)
        if not lgroups:
            return []

        # lgro = [(id,level),(id,level),..]
        group_ids = [g[0] for g in lgroups]

        cur.execute(_get_sql(group_ids, mod))
        #print(_get_sql(group_ids, mod))

        val = _mapping(cur, lgroups)

        # val > [{'col1':'val1',..},{'col1':'val1',..},..]
        if model_group or inp_extend:
            # >> agrego summary al final
            val.append(_get_summary(val))
        else:
            # >> reduzco a summary el estado del grupo
            val = [_get_summary(val)]

        #print('24- val = %s' % val)
        ldata.append((mod, val))

    # res > [(model,[{'col1':'val1',..},{'col1':'val1',..},..]),..]
    #print('25- res = %s' % res)
    return ldata

def _get_models(group_ids):
    # recupero los models...
    lmodels = []
    cur.execute(_get_sql(group_ids, ''))
    for c in cur:
        if c[3] not in lmodels:
            lmodels.append(c[3])
    return lmodels 

def _get_groups(model):
    # recupero los groups...
    lgroups = []
    cur.execute(_get_sql([], model))
    for c in cur:
        #if c[3] not in lmodels:
        lgroups.append(c[1])

    # devuelvo los groups como objeto
    lgroups = pgroups.browse(lgroups)
    return lgroups 

# - - - - - - - - - - -  - - - -

def _get_summary(data):
    #print('100- data = %s' % data)
    gro = _get_object(inp_group) if inp_group else None
    access = {'r':False, 'w':False, 'c':False, 'u':False}

    # data > [{'col1':'val1',..},{'col1':'val1',..},..]
    summ_gro = None
    for d in data:
        if not (isinstance(d[FIELDS[5]],bool)
             or isinstance(d[FIELDS[6]],bool)
             or isinstance(d[FIELDS[7]],bool)
             or isinstance(d[FIELDS[8]],bool)):
             continue

        access['r'] = access['r'] or d[FIELDS[5]]
        access['w'] = access['w'] or d[FIELDS[6]]
        access['c'] = access['c'] or d[FIELDS[7]]
        access['u'] = access['u'] or d[FIELDS[8]]
        summ_gro = gro and gro.id == d[FIELDS[2]] and d

    #FIELDS = ['model','level','id','xml_id','group','read','write','create','unlink']
    #print('101- access = %s' % access)
    summary = {}
    if summ_gro:
        summary = {k:v for k, v in summ_gro.iteritems()}
    elif data:
        default_gro = data[0]
        summary = {
            FIELDS[0]: inp_model if inp_model else default_gro[FIELDS[0]],
            FIELDS[1]: gro.id if gro else default_gro[FIELDS[1]],
            FIELDS[2]: gro.id if gro else default_gro[FIELDS[2]],
            FIELDS[3]: inp_group if inp_group else default_gro[FIELDS[3]],
            FIELDS[4]: gro.name if gro else default_gro[FIELDS[4]],
            FIELDS[5]: False, 
            FIELDS[6]: False, 
            FIELDS[7]: False, 
            FIELDS[8]: False
        }
    else:
        # not data
        summary = {
            FIELDS[0]: inp_model if inp_model else '',
            FIELDS[1]: gro.id if gro else '',
            FIELDS[2]: gro.id if gro else '',
            FIELDS[3]: inp_group if inp_group else '',
            FIELDS[4]: gro.name if gro else '',
            FIELDS[5]: False, 
            FIELDS[6]: False, 
            FIELDS[7]: False, 
            FIELDS[8]: False
        }

    summary[FIELDS[1]] = str(summary[FIELDS[1]])
    summary[FIELDS[5]] = str(access['r']).upper()
    summary[FIELDS[6]] = str(access['w']).upper()
    summary[FIELDS[7]] = str(access['c']).upper()
    summary[FIELDS[8]] = str(access['u']).upper()
    #print('102- summary = %s' % summary)

    # summary > {'col1':'val1',..}
    return summary

def _get_parent(level, group):
    res = []
    new_level = (level+('>' if level else '')+'%s') % group.id

    res.append((group.id,new_level))
    for g in group.implied_ids:
        res += _get_parent(new_level, g)

    return res

def _get_models_groups(model, module_group):
    #print('80-a model = %s' % model)
    #print('80-b module_group = %s' % module_group)

    # --- process models ---
    group = _get_object(module_group) if module_group else None
    #print('81- group = %s' % group)

    group_ids = [group.id] if group else []
    if group:
        # recupero los grupos padres (ascendentes) de este
        # > [g1, g2, g3, ..] > [[{},{},{}], [{},{}], ..]
        lgroups = _get_parent('',group)
        #print('81-a lgro = %s' % lgroups)

        # group_ids = [g1, g2, ..] > [id1, id2, ..] 
        group_ids = [key for key, val in lgroups]
        #print('81-b group_ids = %s' % group_ids)

    lmodels = [model] if model else _get_models(group_ids)
    #print('82- lmodels = %s' % lmodels)

    # check if exisist model
    for mod in lmodels:
        if not _exists_model(mod):
            print('Do not exist model \'' + mod + '\'')
            _close_db()
            sys.exit(1)

    res = []
    for mod in lmodels:
        #print('83- mod = %s' % mod)

        # defino grupo (dado x usuario) o 
        # grupos (recupero los grupos vinculados al model actual)
        lgroups = [group] if group else _get_groups(mod)
        #print('84- lg.groups = %s' % str([g.id for g in lgroups]))

        #print('--- 5.5 ---')
        #print('> lgroups = %s', str(lgroups))
        # por cada grupo recupero sus padres (ascendentes) 
        # > [g1, g2, g3, ..] > [[{},{},{}], [{},{}], ..]
        #lgro = [_get_parent('',g) for g in lgroups]
        lgro = []
        ugroups = []
        for g in lgroups:
            #print('85- g = %s' % g)
            gro = [u for u in ugroups if u['id' == g.id]]
            #print('86- gro = %s' % gro)
            if not gro:
                gro = _get_parent('',g)
                ugroups.append(gro)
            #print('87- gro = %s' % gro)
            #print('88- ugro = %s' % ugroups)
            lgro.append(gro)
            #print('89- lgro = %s' % lgro)

        #print('85- lgro = %s' % lgro[0])

        #print('--- 5.6 ---')
        #print('> lgro = %s', lgro)
        # lo vinculo al modelo actual: [(model, [groups])]
        res.append((mod, lgro[0]))            
        #print('86- res = %s' % res)

    #print('87- res = %s' % res)
    return res

def _get_object(xml_id, type = 'group'):
    """Return the record referenced by this xml_id."""
    module, name = xml_id.split('.')
    #print('get_obj >>  module=%s, name=%s' % (module, name))

    name = type + '_' + name
    search_domain = [('module', '=', module), ('name', '=', name)]
    #print('get_obj >> search=%s' % search_domain)

    data = pdata.read(search_domain, 'model res_id')
    if data:
        assert len(data) == 1
        return client.model(data[0]['model']).get(data[0]['res_id'])

    return False

def _get_reference_groups(lmodels):
    lref = {}
    # > [(model,[group]),..] >> [(model,[{'col1':'val1',..},{'col1':'val1',..},..]),..]
    # >> lgroups = [(id,level),(id,level),..]
    for mod, lgroups in lmodels:

        #print('get_ref >> 1- lgroups = %s' % (lgroups))
        for gid, level in lgroups:
            if lref.get(gid, False):
                continue

            #print('level = %s' % level)
            search_domain = [('model', '=', 'res.groups'), ('res_id', '=', gid)]
            #print('get_ref >> 2- search = %s' % search_domain)
            data = pdata.read(search_domain, 'module name')
            if data:
                assert len(data) == 1
                xml_id = data[0]['module'] + data[0]['name'].replace('group_','.')
                name = _get_object(xml_id).name
                lref.update({gid : (xml_id,name)})
    #print('get_ref >> 4- lref = %s' % lref)
    return lref

# --- print ----
def _info(data, size):
    d = str(data)
    s = int(size)
    diff = s - len(d)
    info = d[:s-1] + '+' if diff < 0 else d + (' ' * diff)
    return info

def _print(ldata):
    # FIELDS = ['model','level','id','xml_id','group','read','write','create','unlink']
    fields = [(FIELDS[k],SIZE[k]) for k in range(len(FIELDS))]

    head = [f[0]+(' '*(f[1]-len(f[0]))) for f in fields]
    sep_head = [('-' * f[1]) for f in fields]
    sep_summary = [('.' * f[1]) for f in fields]

    head = ' '.join(head)
    sep_head = ' '.join(sep_head)
    sep_summary = ' '.join(sep_summary)

    # - - - - - -
    to_print = ['']
    to_print.append(head)
    to_print.append(sep_head)

    fsintax = [('{%s:%s}' % f) for f in fields]
    fsintax = ' '.join(fsintax)

    # - - - - - -
    #print('7- field-sintax = %s' % fsintax)
    #print('8- ldata = %s' % ldata)
    
    #one_model = len(ldata) == 1
    #none_model = not model

    #ldata >> [(model,[{'col1':'val1',..},{'col1':'val1',..},..]),..]
    for mod, data in ldata:
        #print('9- d = %s' % str(d))
        #curr_model = d[0]
        #curr_data  = d[1]

        # data >> [(model,[{'col1':'val1',..},{'col1':'val1',..},..]),..]
        for d in data:
            separa_1 = model_group or inp_extend
            separa_2 = model_group or inp_extend
            last_element = d == data[-1]

            if separa_1 and last_element:
                to_print.append(sep_summary)

            #line = [str(d[f[0]]) + (' ' * (f[1] - len(str(d[f[0]])))) for f in fields]
            line = [_info(d[f[0]], f[1]) for f in fields]
            to_print.append(' '.join(line))

            if separa_2 and last_element:
                to_print.append('')

    for p in to_print:
        print(p)
    
# --- db ---
def _open_db():
    server, db, user, psw = erppeek.read_config(CONFIG_FILE)
    conn = psycopg2.connect(dbname=db, user=USER_DB, password=PSW_DB, host=SERVER)
    cur = conn.cursor()
    return conn, cur

def _close_db():
    cur.close()
    conn.close()

# main -------------------------------------------------------
if __name__ != "__main__":
    sys.exit(1)

# ----------------------------------------
path = str(sys.argv[0]).split('/')
file = path[len(path)-1].strip()
path = '/'.join(path[:len(path)-1]).strip() 
current_path = os.getcwd()

os.chdir(path)
client = erppeek.Client.from_config(CONFIG_FILE)
os.chdir(path)

# set proxys ----------------
pmodel  = client.model('ir.model')
pgroups = client.model('res.groups')
pdata   = client.model('ir.model.data')

# check arguments
inp_extend, inp_model, inp_group = _check_argum()
#print('main-1- model = %s, group = %s' % (inp_model, inp_group))

model_group = inp_model and inp_group

# 
conn, cur = _open_db()

# get models + groups > [(model,[groups]), ..] > [(model, [{}, {}, ..])]
lmodels = _get_models_groups(inp_model, inp_group)
#print('main-2- lmodels = %s' % lmodels)

# recupero las referencias de cada grupo: 'model.name'
lref = _get_reference_groups(lmodels)
#print('main-3- lref = %s' % lref)

# recupero los datos (por model y grupos) y proceso > [(model,[group]),..]
# >> [(model,[{'col1':'val1',..},{'col1':'val1',..},..]),..]
ldata = _process_model_groups(lmodels)
#print('main-4- ldata = %s' % ldata)

_close_db()
#print('main-5- ldata = %s' % ldata)

# imprimo...
_print(ldata)

sys.exit(0)

